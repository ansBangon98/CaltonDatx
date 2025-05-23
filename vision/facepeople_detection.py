# import time
import cv2
import numpy as np
import core.state as state
from tools.tracker import Sort


class Detection():
    def __init__(self):
        self.models = state.models
        self.appcont = state.appcont
        self.tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)
    
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

            if cls_id == 0 and cls_conf >= 0.85:
                    face_bbox.append([x1, y1, x2, y2])
            else:
                if cls_conf >= 0.7:
                    people_bbox.append([x1, y1, x2, y2])
        return face_bbox, people_bbox

    def _get_detection(self, frame):
        fw = frame.shape[1]
        fh = frame.shape[0]
        
        size = 320
        resize_frame = cv2.resize(frame.copy(), (size, size))
        blob = resize_frame.transpose(2, 0, 1)
        blob = np.expand_dims(blob, axis=0).astype(np.float32) / 255.0

        self.models.facpep_interpreter.set_tensor(self.models.facpep_input_details[0]['index'], blob)
        self.models.facpep_interpreter.invoke()
        outputs = self.models.facpep_interpreter.get_tensor(self.models.facpep_output_details[0]['index'])

        # Run TFLite inference
        interpreter = self.models.facpep_interpreter
        input_index = self.models.facpep_input_details[0]['index']
        interpreter.set_tensor(input_index, blob)
        interpreter.invoke()

        output_data = []
        for output_detail in self.models.facpep_output_details:
            output = interpreter.get_tensor(output_detail['index'])
            output_data.append(output)
        
        bbox = self.__post_processing(output_data)
        face_bbox, people_bbox = self.__get_bounding_box(bbox, fw, fh)

        if 'Face' in self.appcont._detection and 'Body' in self.appcont._detection:
            detection_coords = {}
            if people_bbox:
                trk = self.tracker.update(np.array(people_bbox))
                for coords_trk in trk:
                    bx1, by1, bx2, by2, id = map(int, coords_trk)
                    is_face_detected = False
                    for face_coords in face_bbox:
                        fx1, fy1, fx2, fy2 = face_coords
                        if fx1 > bx1 and fx2 < bx2 and fy1 > by1 and fy2 < by2:
                            detection_coords[id] = {
                                'body_coords': [bx1, by1, bx2, by2],
                                'face_coords': [fx1, fy1, fx2, fy2]
                            }
                            is_face_detected = True
                            break
                    if not is_face_detected:
                        detection_coords[id] = {
                            'body_coords': [bx1, by1, bx2, by2],
                            'face_coords': [None, None, None, None]
                        }
            for id, item in detection_coords.items():
                bx1, by1, bx2, by2 = item['body_coords']
                self.__create_body_box(frame, bx1, by1, bx2, by2)  # Body bounding box
                if item['face_coords'] == [None, None, None, None]:
                    pass
                    # self._captured_data(id, 'OTS')
                    # self.__OTS_caption_display(bx1, by1, id, frame)
                else:
                    fx1, fy1, fx2, fy2 = item['face_coords']
                    # self.__analytic_captured_data(id, fx1, fy1, fx2, fy2, fh, fw)
                    # self.__display_predictions(bx1, by1, bx2, by2, id, frame)
                    self.__create_face_box(frame, fx1, fy1, fx2, fy2)  # Face bounding box
        
        return frame
    
    def __create_face_box(self, frame, x1, y1, x2, y2):

        thick = 2
        thick_width = 15
        line_color = (0, 255, 0)

        cv2.line(frame, (x1, y1), (x1 + thick_width, y1), line_color, thick)  # Left-Top Line
        cv2.line(frame, (x1, y1), (x1, y1 + thick_width), line_color, thick)  # Left-Side

        cv2.line(frame, (x2, y1), (x2 - thick_width, y1), line_color, thick)  # Right-Top Line
        cv2.line(frame, (x2, y1), (x2, y1 + thick_width), line_color, thick)  # Right-Side

        cv2.line(frame, (x1, y2), (x1 + thick_width, y2), line_color, thick)  # Left-Boto Line
        cv2.line(frame, (x1, y2), (x1, y2 - thick_width), line_color, thick)  # Left-Side

        cv2.line(frame, (x2, y2), (x2 - thick_width, y2), line_color, thick)  # Right-Top Line
        cv2.line(frame, (x2, y2), (x2, y2 - thick_width), line_color, thick)  # Right-Side

    def __create_body_box(self, frame, x1, y1, x2, y2):
        rectangle_color = (255, 0, 255)
        line_color = (0, 255, 0)
        line_width = 10
        line_tickness = 2
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), rectangle_color, 1)

        cv2.line(frame, (x1, y1), (x1 + line_width, y1), line_color, thickness=line_tickness)  # Left-Top Line
        cv2.line(frame, (x1, y1), (x1, y1 + line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x2, y1), (x2 - line_width, y1), line_color, thickness=line_tickness)  # Right-Top Line
        cv2.line(frame, (x2, y1), (x2, y1 + line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x1, y2), (x1 + line_width, y2), line_color, thickness=line_tickness)  # Left-Boto Line
        cv2.line(frame, (x1, y2), (x1, y2 - line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x2, y2), (x2 - line_width, y2), line_color, thickness=line_tickness)  # Right-Top Line
        cv2.line(frame, (x2, y2), (x2, y2 - line_width), line_color, thickness=line_tickness)  # Lef-Side