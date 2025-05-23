import cv2
import core.state as state

from kivy.clock import Clock
from kivy.graphics.texture import Texture

class Camera():
    def __init__(self):
        self._frame = None
        self._event = None
        self.__capture = None
    
    def _update(self, dt):
        if self.__capture and self.__capture.isOpened():
            ret, frame = self.__capture.read()
            if ret:
                frame = state.detection._get_detection(frame)
                buf = cv2.flip(frame, 0).tobytes()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self._frame = image_texture
    
    def _start_camera(self, camsource):
        if self.__capture is None:
            self.__capture = cv2.VideoCapture(camsource, cv2.CAP_DSHOW)
            self._event = Clock.schedule_interval(self._update, 1.0 / 30)
    
    def _stop_camera(self):
        if self.__capture:
            self._event.cancel()
            self.__capture.release()
            self.__capture = None
            self._frame = None