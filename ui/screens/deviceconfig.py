import os
import sys

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
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


class DeviceConfig(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.opt_camselected = None

    def _on_click_start(self):
        if self.opt_camselected is None:
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the device camera.').open()
        elif self.opt_camselected == 'network' and self.ids.txt_rtsp.text == '':
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please enter the RTSP/Link CCTV address.').open()
        elif self.opt_camselected == 'camera' and self.ids.drp_cameras.text == 'Select an option':
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the camera.').open()
        elif self.ids.drp_resolution.text == 'Select an option':
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the resolution.').open()
        elif self.ids.drp_orientation.text == 'Select an option':
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text='Please select the orientation.').open()
    
    def _on_press_cam_ref(self):
        self.opt_camselected = 'network' if self.ids.opt_network.state == 'down' else 'camera'
        print(self.opt_camselected)
    
    def _on_click_close(self):
        Factory.ShowMessage_Ask(title='CONFIRMATION', message_text='Are you sure do you want to close this program?').open()

