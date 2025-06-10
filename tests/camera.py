import time
import cv2
import threading
import numpy as np

from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.load_models import Models
from vision.detections import Detection
from vision.predictions import Gender, Age, Emotion
from vision.displays import Caption, Track
from app.controller import AppController

import core.state as state

class KivyCam(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        state.appcont = AppController(None)
        state.models = Models()
        state.detection = Detection()
        state.gender = Gender()
        state.age = Age()
        state.emotion = Emotion()

        state.caption = Caption()
        state.track = Track()

        # Image widget to display video frames
        self.image = Image()
        self.add_widget(self.image)

        # Start/Stop buttons
        self.btn_layout = BoxLayout(size_hint=(1, 0.2))
        self.start_btn = Button(text="Start Camera")
        self.stop_btn = Button(text="Stop Camera")
        self.btn_layout.add_widget(self.start_btn)
        self.btn_layout.add_widget(self.stop_btn)
        self.add_widget(self.btn_layout)

        # Event bindings
        self.start_btn.bind(on_press=self.start_camera)
        self.stop_btn.bind(on_press=self.stop_camera)

        # Camera attributes
        self.capture = None
        self.event = None

        self.fps_count = 0
        self.fps_start = time.time()

        self.detection = None
        self.prediction = {}
        self.frame = None

        threading.Thread(target=self.get_detection).start()

    def get_detection(self):
        while True:
            if self.frame is not None:
                self.detection = state.detection._get_detection(self.frame)
                if self.detection:
                    face_box =  {id:item for id, item in self.detection.items() if item['face_coords'] != [None, None, None, None]}
                    for id, item in face_box.items():
                        fx1, fy1, fx2, fy2 = item['face_coords']
                        # bx1, by1, bx2, by2 = item['body_coords']
                        height, width, _ = self.frame.shape
                        fx1 = max(0, fx1)
                        fy1 = max(0, fy1)
                        fx2 = min(width, fx2)
                        fy2 = min(height, fy2)
                        face = self.frame[fy1:fy2, fx1:fx2]
                        age = state.age._predic_age(face, id)
                        gender = state.gender._predic_gender(face, id)
                        emotion = state.emotion._predic_emotion(face, id)

                        self.prediction[id] = {
                            'gender': gender if gender is not None else self.prediction[id]['gender'] if id in self.prediction else '',
                            'age': age if age is not None else self.prediction[id]['age'] if id in self.prediction else '',
                            'emotion': emotion if emotion is not None else self.prediction[id]['emotion'] if id in self.prediction else ''
                        }

    def start_camera(self, *args):
        self.fps_count = 0
        self.fps_start = time.time()
        if self.capture is None:
            self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.event = Clock.schedule_interval(self.update, 1.0 / 30)

    def stop_camera(self, *args):
        if self.capture:
            self.event.cancel()
            self.capture.release()
            self.capture = None
            self.image.texture = None  # Clear the image

    def update(self, dt):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.frame = frame.copy()
                if self.detection is not None:
                    for id, item in self.detection.items():
                        prediction = None
                        if id in self.prediction:
                            prediction = self.prediction[id]
                        if prediction is not None:
                            gender = prediction['gender']
                            age = prediction['age']
                            emotion = prediction['emotion']

                        if item['face_coords'] != [None, None, None, None]:
                            x1, y1, x2, y2 = item['face_coords']
                            frame = state.track._create_face_box(frame, x1, y1, x2, y2)
                            if item['body_coords'] == [None, None, None, None]:
                                if prediction is not None:
                                    if gender != '':
                                        frame = state.caption._display_caption(age, x2, y1, frame)
                                        frame = state.caption._display_caption(gender, x2, y1+30, frame)

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
                fps = self.fps_count / (fps_end_time - self.fps_start)
                fps_label = f"FPS: {fps:.2f}"
                cv2.putText(frame, fps_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                self.fps_count += 1

                buf = cv2.flip(frame, 0).tobytes()
                img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.image.texture = img_texture


class MainApp(App):
    def build(self):
        return KivyCam()


if __name__ == '__main__':
    MainApp().run()
