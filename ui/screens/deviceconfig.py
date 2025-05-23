import time
import cv2
import os
import sys
import core.state as state

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from ui.widgets.tools import TextCanvasWidget
from ui.widgets.popup import *



# 869, 754
Window.size = (869, 754)
Window.minimum_width = 869
Window.minimum_height = 754

Window.clearcolor = (1, 1, 1, 1)


# def on_window_resize(instance, value):
#     print(f"Window resized to: {value}")

# Window.bind(size=on_window_resize)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

deviceconfig_FILE = resource_path("ui/kv/deviceconfig.kv")
Builder.load_file(deviceconfig_FILE)

class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        Animation(size=(36, 36), d=0.1).start(self)

    def on_release(self):
        Animation(size=(40, 40), d=0.1).start(self)

class DeviceConfig(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cam_bg = self.capture_background()
        self.appcont = state.appcont
        self.__cam_event = None
        self._opt_camselected = ''
        self.ids.img_camera.texture = self.cam_bg

    def capture_background(self):
        image = cv2.imread("./assets/deviceconfig/cam_bg.png")
        buf = cv2.flip(image, 0).tobytes()
        image_texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return image_texture

    def _on_click_start(self, instance):
        # if not self._opt_camselected:
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the device camera.').open()
        # elif self._opt_camselected == 'network' and self.ids.txt_rtsp.text == '':
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please enter the RTSP/Link CCTV address.').open()
        # elif self._opt_camselected == 'camera' and self.ids.drp_cameras.text == 'Select an option':
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the camera.').open()
        # elif self.ids.drp_resolution.text == 'Select an option':
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the display resolution.').open()
        # elif self.ids.drp_orientation.text == 'Select an option':
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the view orientation.').open()
        # elif not self._detection:
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the analytic detection.').open()
        # elif not self._prediction:
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the analytic prediction.').open()
        # elif not self._ageclassification:
        #     Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the analytic age classification.').open()
        # else:
        Window.set_system_cursor('wait')
        if instance.text == 'Start':
            instance.text = 'Stop'    
            self.appcont.camera._start_camera(0)
            self.__cam_event = Clock.schedule_interval(self._get_capture_frame, 1.0/30)
        else:
            instance.text = 'Start'
            self.appcont.camera._stop_camera()
            self.__cam_event.cancel()
            self.ids.img_camera.texture = self.cam_bg
        Window.set_system_cursor('arrow')
    
    
    def _on_press_cam_ref(self):
        self._opt_camselected = 'network' if self.ids.opt_network.state == 'down' else 'camera'
        print(self._opt_camselected)
    
    def _on_click_close(self):
        Factory.ShowMessage_Ask(title='CONFIRMATION', message_text='Are you sure do you want to close this program?').open()

    def _get_capture_frame(self, dt):
        if self.appcont.camera._frame is not None:
            self.ids.img_camera.texture = self.appcont.camera._frame

