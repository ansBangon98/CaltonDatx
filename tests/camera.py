import time
import cv2
import threading
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
from vision.facepeople_detection import Detection
from app.controller import AppController

import core.state as state

class KivyCam(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        state.appcont = AppController(None)
        state.models = Models()
        state.detection = Detection()

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

    def start_camera(self, *args):
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
                # Convert image to texture
                frame = state.detection._get_detection(frame)
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
