import os
import sys
import core.state as state

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation


from ui.widgets.tools import TextCanvasWidget
from ui.widgets.popup import *

Window.size = (869, 754)
Window.minimum_width = 869
Window.minimum_height = 754

Window.clearcolor = (1, 1, 1, 1)

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
        self.appcont = state.appcont
    

    def _on_click_start(self):
        is_valid, error = self.appcont._validate_input_data()
        if not is_valid:
            Factory.ShowMessage_Info(title='INCOMPLETE', message_text=error).open()
        else:
            self.appcont._start_stop_camera()
    
    def _on_click_close(self):
        Factory.ShowMessage_Ask(title='CONFIRMATION', message_text='Are you sure do you want to close this program?').open()
    
    def _ckbx_body_check_changed(self):
        detection = self.appcont.detection._detection
        if self.ids.ckbx_body.active:
            if 'Body' not in detection:
                detection.append('Body')
        else:
            if 'Body' in detection:
                detection.remove('Body')
        
    def _ckbx_face_check_changed(self):
        detection = self.appcont.detection._detection
        if self.ids.ckbx_face.active:
            if 'Face' not in detection:
                detection.append('Face')
        else:
            if 'Face' in detection:
                detection.remove('Face')
        