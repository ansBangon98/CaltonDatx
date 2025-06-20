import cv2
import time
import threading
import core.state as state

from kivy.clock import Clock
from kivy.graphics.texture import Texture


class Camera():
    def __init__(self):
        self._event = None
        self.__capture = None

        self.__fps_count = 0
        self.__fps_start = time.time()

        self.__detection = None
        self.__prediction = {}
        self.__frame = None
        self._image = None

        self.__is_thread = False
    
    def __get_detection(self):
        while self.__is_thread:
            if self.__frame is not None:
                self.__detection = state.detection._get_detection(self.__frame)
                if self.__detection:
                    face_box =  {id:item for id, item in self.__detection.items() if item['face_coords'] != [None, None, None, None]}
                    for id, item in face_box.items():
                        fx1, fy1, fx2, fy2 = item['face_coords']
                        height, width, _ = self.__frame.shape
                        fx1 = max(0, fx1)
                        fy1 = max(0, fy1)
                        fx2 = min(width, fx2)
                        fy2 = min(height, fy2)
                        face = self.__frame[fy1:fy2, fx1:fx2]
                        age = state.age._predic_age(face, id)
                        gender = state.gender._predic_gender(face, id)
                        emotion = state.emotion._predic_emotion(face, id)

                        self.__prediction[id] = {
                            'age': age if age is not None else self.__prediction[id]['age'] if id in self.__prediction else '',
                            'gender': gender if gender is not None else self.__prediction[id]['gender'] if id in self.__prediction else '',
                            'emotion': emotion if emotion is not None else self.__prediction[id]['emotion'] if id in self.__prediction else ''
                        }

    def _update(self, dt):
        if self.__capture and self.__capture.isOpened():
            ret, frame = self.__capture.read()
            if ret:
                self.__frame = frame.copy()
                if self.__detection is not None:
                    for id, item in self.__detection.items():
                        prediction = None
                        if id in self.__prediction:
                            prediction = self.__prediction[id]
                        if prediction is not None:
                            age = prediction['age']
                            gender = prediction['gender']
                            emotion = prediction['emotion']

                        if item['face_coords'] != [None, None, None, None]:
                            x1, y1, x2, y2 = item['face_coords']
                            frame = state.track._create_face_box(frame, x1, y1, x2, y2)
                            if item['body_coords'] == [None, None, None, None]:
                                if prediction is not None:
                                    if gender != '':
                                        frame = state.caption._display_caption(age, x2, y1, frame)
                                        frame = state.caption._display_caption(gender, x2, y1+30, frame)
                                        frame = state.caption._display_caption(emotion, x2, y1+60, frame)

                        if item['body_coords'] != [None, None, None, None]:
                            x1, y1, x2, y2 = item['body_coords']
                            frame = state.track._create_body_box(frame, x1, y1, x2, y2)
                            if item['face_coords'] != [None, None, None, None]:
                                if prediction is not None:
                                    if gender != '':
                                        frame = state.caption._display_caption(age, x1, y1, frame)
                                        frame = state.caption._display_caption(gender, x1, y1+30, frame)
                                        frame = state.caption._display_caption(emotion, x1, y1+60, frame)
                
                fps_end_time = time.time()
                fps = self.__fps_count / (fps_end_time - self.__fps_start)
                fps_label = f"FPS: {fps:.2f}"
                cv2.putText(frame, fps_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                self.__fps_count += 1

                buf = cv2.flip(frame, 0).tobytes()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self._image = image_texture
    
    def _start_camera(self, camsource):
        if self.__capture is None:
            self.__fps_count = 0
            self.__fps_start = time.time()
            self.__is_thread = True
            threading.Thread(target=self.__get_detection).start()
            self.__capture = cv2.VideoCapture(camsource, cv2.CAP_DSHOW)
            self._event = Clock.schedule_interval(self._update, 1.0 / 30)
    
    def _stop_camera(self):
        if self.__capture:
            self.__is_thread = False
            self._event.cancel()
            self.__capture.release()
            self.__capture = None
            self.__detection = None
            self.__prediction = {}
            self.__frame = None
            self._image = None