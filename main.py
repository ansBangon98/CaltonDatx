

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from app.controller import AppController
from vision.load_models import Models
from app.camera import Camera
from vision.detections import Detection
from vision.predictions import Gender, Age, Emotion
from vision.displays import Caption, Track

import core.state as state

class CaltonDatx(App):
    def build(self):
        state.camera = Camera()
        state.models = Models()
        state.detection = Detection()

        self.sm = ScreenManager()
        controller = AppController(screen_manager=self.sm)
        state.appcont = controller
        
        state.gender = Gender()
        state.age = Age()
        state.emotion = Emotion()

        state.caption = Caption()
        state.track = Track()
        
        controller._load_initial_screen()
        return self.sm

if __name__=="__main__":
    CaltonDatx().run()

    
# from tests.camera import MainApp

# if __name__=="__main__":
#     MainApp().run()