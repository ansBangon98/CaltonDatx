# import time
import cv2
import numpy as np
import core.state as state
from tools.tracker import Sort


class Detection():
    def __init__(self):
        self.models = state.models

        self.interpreter = state.models.facpep_interpreter
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

        self._detection = ['Face', 'Body']
        # self._detection = ['Face']
    
    def __nms_cpu(self, boxes, confs, nms_thresh=0.5, min_mode=False):
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = confs.argsort()[::-1]

        keep = []
        while order.size > 0:
            idx_self = order[0]
            idx_other = order[1:]

            keep.append(idx_self)

            xx1 = np.maximum(x1[idx_self], x1[idx_other])
            yy1 = np.maximum(y1[idx_self], y1[idx_other])
            xx2 = np.minimum(x2[idx_self], x2[idx_other])
            yy2 = np.minimum(y2[idx_self], y2[idx_other])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            if min_mode:
                over = inter / np.minimum(areas[order[0]], areas[order[1:]])
            else:
                over = inter / (areas[order[0]] + areas[order[1:]] - inter)

            inds = np.where(over <= nms_thresh)[0]
            order = order[inds + 1]

        return np.array(keep)

    def __post_processing(self, output, conf_thresh=0.4, nms_thresh=0.6):
        box_array = output[0]
        confs = output[1]
        if type(box_array).__name__ != 'ndarray':
            box_array = box_array.cpu().detach().numpy()
            confs = confs.cpu().detach().numpy()

        num_classes = confs.shape[2]
        box_array = box_array[:, :, 0]
        max_conf = np.max(confs, axis=2)
        max_id = np.argmax(confs, axis=2)

        bboxes_batch = []
        for i in range(box_array.shape[0]):
            argwhere = max_conf[i] > conf_thresh
            l_box_array = box_array[i, argwhere, :]
            l_max_conf = max_conf[i, argwhere]
            l_max_id = max_id[i, argwhere]

            bboxes = []
            for j in range(num_classes):

                cls_argwhere = l_max_id == j
                ll_box_array = l_box_array[cls_argwhere, :]
                ll_max_conf = l_max_conf[cls_argwhere]
                ll_max_id = l_max_id[cls_argwhere]

                keep = self.__nms_cpu(ll_box_array, ll_max_conf, nms_thresh)

                if (keep.size > 0):
                    ll_box_array = ll_box_array[keep, :]
                    ll_max_conf = ll_max_conf[keep]
                    ll_max_id = ll_max_id[keep]

                    for k in range(ll_box_array.shape[0]):
                        bboxes.append(
                            [ll_box_array[k, 0], ll_box_array[k, 1], ll_box_array[k, 2], ll_box_array[k, 3],
                             ll_max_conf[k], ll_max_id[k]])

            bboxes_batch.append(bboxes)
        return bboxes_batch[0]
    
    def __get_bounding_box(self, detection,  fw, fh):
        face_bbox = []
        people_bbox = []
        for i in range(len(detection)):
            box = detection[i]
            x1 = int(box[0] * fw)
            y1 = int(box[1] * fh)
            x2 = int(box[2] * fw)
            y2 = int(box[3] * fh)
            cls_conf = box[4]
            cls_id = box[5]

            if cls_id == 0 and cls_conf >= 0.6:
                face_bbox.append([x1, y1, x2, y2])
            else:
                if cls_conf >= 0.5:
                    people_bbox.append([x1, y1, x2, y2])
        return face_bbox, people_bbox

    def _get_detection(self, frame):
        fw = frame.shape[1]
        fh = frame.shape[0]
        
        size = 320
        resize_frame = cv2.resize(frame.copy(), (size, size))
        blob = resize_frame.transpose(2, 0, 1)
        blob = np.expand_dims(blob, axis=0).astype(np.float32) / 255.0

        # interpreter = self.models.facpep_interpreter
        # input_index = self.models.facpep_input_details[0]['index']
        self.interpreter.set_tensor(self.input_details[0]['index'], blob)
        self.interpreter.invoke()
        output_data = [self.interpreter.get_tensor(output['index']) for output in self.output_details]
        bbox = self.__post_processing(output_data)
        face_bbox, people_bbox = self.__get_bounding_box(bbox, fw, fh)

        detection_coords = {}
        face_with_body, face_and_body = [], []
        is_has_face_body = 'Face' in self._detection and 'Body' in self._detection
        # if 'Face' in self._detection and 'Body' in self._detection:
        if is_has_face_body:
            for pbbox in people_bbox:
                px1, py1, px2, py2 = pbbox
                for i in range(len(face_bbox)):
                    fx1, fy1, fx2, fy2 = face_bbox[i]
                    if fx1 > px1 and fx2 < px2 and fy1 > py1 and fy2 < py2:
                        face_with_body.append([fx1, fy1, fx2, fy2])
                        del face_bbox[i]
                        break
        
        face_coords_list = []
        for item in face_bbox:
            x1, y1, x2, y2 = item
            face_coords_list.append(f"{x1}{y1}{x2}{y2}")

        bounding_box = face_bbox+people_bbox if is_has_face_body else face_bbox if 'Face' in self._detection else people_bbox
        
        if bounding_box:
            trk = self.tracker.update(np.array(bounding_box))
            for coords_trk in trk:
                x1, y1, x2, y2, id = map(int, coords_trk)
                ishasbody = False
                if is_has_face_body:
                    for i in range(len(face_with_body)):
                        fx1, fy1, fx2, fy2 = face_with_body[i]
                        if fx1 > x1 and fx2 < x2 and fy1 > y1 and fy2 < y2:
                            detection_coords[id] = {
                                'body_coords': [x1, y1, x2, y2],
                                'face_coords': [fx1, fy1, fx2, fy2]
                                }
                            ishasbody = True
                            del face_with_body[i]
                            break
                if not ishasbody:
                    coords = f"{x1}{y1}{x2}{y2}"
                    if coords in face_coords_list:
                        detection_coords[id] = {
                        'body_coords': [None, None, None, None],
                        'face_coords': [x1, y1, x2, y2]
                        }
                    else:
                        detection_coords[id] = {
                        'body_coords': [x1, y1, x2, y2],
                        'face_coords': [None, None, None, None]
                        }


        """
        if 'Face' in self._detection and 'Body' in self._detection:
            if people_bbox:
                face_with_body, face_and_body = [], []
                for pbbox in people_bbox:
                    px1, py1, px2, py2 = pbbox
                    for i in range(len(face_bbox)):
                        fx1, fy1, fx2, fy2 = face_bbox[i]
                        if fx1 > px1 and fx2 < px2 and fy1 > py1 and fy2 < py2:
                            face_with_body.append([fx1, fy1, fx2, fy2])
                            del face_bbox[i]
                            break
                
                face_coords_list = []
                for item in face_bbox:
                    x1, y1, x2, y2 = item
                    face_coords_list.append(f"{x1}{y1}{x2}{y2}")


                face_and_body = face_bbox+people_bbox if face_bbox else people_bbox
                trk = self.tracker.update(np.array(face_and_body))
                for coords_trk in trk:
                    x1, y1, x2, y2, id = map(int, coords_trk)
                    ishasbody = False
                    for i in range(len(face_with_body)):
                        fx1, fy1, fx2, fy2 = face_with_body[i]
                        if fx1 > x1 and fx2 < x2 and fy1 > y1 and fy2 < y2:
                            detection_coords[id] = {
                                'body_coords': [x1, y1, x2, y2],
                                'face_coords': [fx1, fy1, fx2, fy2]
                                }
                            ishasbody = True
                            del face_with_body[i]
                            break
                    if not ishasbody:
                        coords = f"{x1}{y1}{x2}{y2}"
                        if coords in face_coords_list:
                            detection_coords[id] = {
                            'body_coords': [None, None, None, None],
                            'face_coords': [x1, y1, x2, y2]
                            }
        """
        return detection_coords