import numpy as np
import threading

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.load_models import Models
from vision.detections import Detection

import core.state as state

from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.core.text import Label as CoreLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window

class FaceDetectApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame = None
        state.models = Models()
        state.detection = Detection()
        self.detection = None
        threading.Thread(target=self.get_detection).start()

    def get_detection(self):
        while True:
            if self.frame is not None:
                self.detection = state.detection._get_detection(self.frame)

    def build(self):
        self.layout = BoxLayout()
        self.camera = Camera(resolution=(640, 480), play=True)
        self.image = Image()
        self.layout.add_widget(self.image)

        # Schedule updates
        Clock.schedule_interval(self.update, 1.0 / 30)  # 15 FPS is more than enough for mobile
        return self.layout

    def draw_text(self, widget, text, x, y, font_size=20, color=(1, 1, 1, 1)):
        label = CoreLabel(text=text, font_size=font_size)
        label.refresh()
        texture = label.texture
        texture_size = texture.size

        with widget.canvas.after:
            Color(*color)  # RGBA
            Rectangle(texture=texture, pos=(x, y), size=texture_size)

    def update(self, dt):
        if not self.camera.texture:
            return

        # Get image from Kivy camera
        texture = self.camera.texture
        size = texture.size
        # print(size)
        pixels = texture.pixels

        frame = np.frombuffer(pixels, dtype=np.uint8)
        frame = frame.reshape((size[1], size[0], 4))[:, :, :3].copy()
        self.frame = frame.copy()

        # Clear previous drawings
        self.image.canvas.after.clear()
        win_w, win_h = Window.size
        dis_w, dis_h = self.image.size
        if self.detection is not None:
            with self.image.canvas.after:
                for id, item in self.detection.items():
                    if item['face_coords'] != [None, None, None, None]:
                        x1, y1, x2, y2 = item['face_coords']
                        # norm_x1 = x1 / size[0]
                        # norm_y1 = y1 / size[1]
                        # norm_x2 = x2 / size[0]
                        # norm_y2 = y2 / size[1]

                        # x = norm_x1 * dis_w
                        # y = (1 - norm_y2) * dis_h  # flip y-axis for Kivy
                        # w = (norm_x2 - norm_x1) * dis_w
                        # h = (norm_y2 - norm_y1) * dis_h
                        
                        
                        x = x1 + (win_w-size[0]) / 2
                        y = (size[1] - y2) + (win_h-size[1]) / 2
                        w = x2 - x1
                        h = y2 - y1

                        self.draw_text(self.image, "Male", x, y + h + 10)

                        Color(0.3333, 0.0078, 0.9804)
                        Line(rectangle=(x, y, w, h), width=1)

                        corner_len = min(w, h) * 0.15  # 25% of side
                        Color(0, 1, 0)
                        # Top-left corner
                        Line(points=[x, y + h, x + corner_len, y + h], width=2)  # ─
                        Line(points=[x, y + h, x, y + h - corner_len], width=2)  # │

                        # Top-right corner
                        Line(points=[x + w, y + h, x + w - corner_len, y + h], width=2)
                        Line(points=[x + w, y + h, x + w, y + h - corner_len], width=2)

                        # Bottom-left corner
                        Line(points=[x, y, x + corner_len, y], width=2)
                        Line(points=[x, y, x, y + corner_len], width=2)

                        # Bottom-right corner
                        Line(points=[x + w, y, x + w - corner_len, y], width=2)
                        Line(points=[x + w, y, x + w, y + corner_len], width=2)

                        # Line(rectangle=(x, y, w, h), width=2)
        frame = np.flip(frame, axis=0)
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.image.texture = texture

    def on_stop(self):
        pass

if __name__ == "__main__":
    FaceDetectApp().run()
