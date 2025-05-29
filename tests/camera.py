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
from vision.facepeople_detection import Detection
from vision.gender import Gender
from app.controller import AppController

import core.state as state

class KivyCam(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        state.appcont = AppController(None)
        state.models = Models()
        state.detection = Detection()
        state.gender = Gender()

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
        self.frame = None

        threading.Thread(target=self.get_detection).start()

    def get_detection(self):
        while True:
            if self.frame is not None:
                self.detection = state.detection._get_detection(self.frame)
                if self.detection:
                    face_box =  {id:item['face_coords'] for id, item in self.detection.items() if item['face_coords'] != [None, None, None, None]}
                    for id, item in face_box.items():
                        x1, y1, x2, y2 = item
                        face = self.frame[y1:y2, x1:x2]
                        gender = state.gender._predic_gender(face)
                        print(gender)
                        stoper = ''
            # time.sleep(5 / 1000)

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

    def update(self, dt):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                # Convert image to texture
                self.frame = frame.copy()

                if self.detection is not None:
                    for id, item in self.detection.items():
                        bx1, by1, bx2, by2 = item['body_coords']
                        self.__create_body_box(frame, bx1, by1, bx2, by2)  # Body bounding box
                        if item['face_coords'] == [None, None, None, None]:
                            pass
                        else:
                            fx1, fy1, fx2, fy2 = item['face_coords']
                            self.__create_face_box(frame, fx1, fy1, fx2, fy2)  # Face bounding box

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
