import time
import numpy as np
import threading
import core.state as state

from PIL import Image, ImageDraw, ImageFont
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera as webCam


class Camera():
    def __init__(self):
        self._event = None
        self.__webcam = webCam(play=False)

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

    def _set_image_orientation(self, frame):
        image = Image.fromarray(frame)
        angle = int(state.appcont.ids.drp_orientation.text)
        rotate_image = image.rotate(angle, expand=True)
        return np.array(rotate_image)


    def _capture_camera_view(self):
        if self.__webcam.texture:
            texture = self.__webcam.texture
            size = texture.size
            pixels = texture.pixels

            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape((size[1], size[0], 4))[:, :, :3].copy()
            frame = self._set_image_orientation(frame)
            self.__frame = frame.copy()
            # frame = np.flip(frame, axis=0)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self._image = texture
    
    def _rotate_image(self):
        frame = self._set_image_orientation(self.__frame)
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self._image = texture

    def _update(self, dt):
        if self.__webcam.texture:
            texture = self.__webcam.texture
            size = texture.size
            pixels = texture.pixels

            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape((size[1], size[0], 4))[:, :, :3].copy()
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
                        x1, y1, _, _ = item['face_coords']
                        frame = state.track._create_face_box(frame, item['face_coords'])
                        if item['body_coords'] == [None, None, None, None]:
                            if prediction is not None:
                                if gender != '':
                                    frame = state.caption._display_caption(frame, [x1, y1], age)
                                    frame = state.caption._display_caption(frame, [x1, y1+10], gender)
                                    frame = state.caption._display_caption(frame, [x1, y1+20], emotion)

                    if item['body_coords'] != [None, None, None, None]:
                        x1, y1, _, _ = item['body_coords']
                        frame = state.track._create_body_box(frame, item['body_coords'])
                        if item['face_coords'] != [None, None, None, None]:
                            if prediction is not None:
                                if gender != '':
                                    frame = state.caption._display_caption(frame, [x1, y1], age)
                                    frame = state.caption._display_caption(frame, [x1, y1+15], gender)
                                    frame = state.caption._display_caption(frame, [x1, y1+30], emotion)
                
                image = Image.fromarray(frame)
                image_draw = ImageDraw.Draw(image)
                color = (0, 0, 0)
                font = ImageFont.truetype('./assets/fonts/Roboto-Regular.ttf', 17)
                fps_end_time = time.time()
                fps = self.__fps_count / (fps_end_time - self.__fps_start)
                fps_label = f"FPS: {fps:.2f}"
                image_draw.text((10, 10), fps_label, fill=color, font=font)
                frame = np.array(image)
                self.__fps_count += 1

                frame = np.flip(frame, axis=0)
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
                self._image = texture
    
    def _start_camera(self, camsource):
        self.__fps_count = 0
        self.__fps_start = time.time()
        self.__is_thread = True
        self.__webcam.play = True
        threading.Thread(target=self.__get_detection).start()
        self._event = Clock.schedule_interval(self._update, 1.0 / 30)
    
    def _stop_camera(self):
        if self.__webcam.texture:
            self.__is_thread = False
            self._event.cancel()
            self.__detection = None
            self.__prediction = {}
            self.__frame = None
            self._image = None