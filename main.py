from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from app.controller import AppController
from vision.load_models import Models
from app.camera import Camera
from vision.facepeople_detection import Detection

import core.state as state


class CaltonDatx(App):
    def build(self):
        state.camera = Camera()

        self.sm = ScreenManager()
        controller = AppController(screen_manager=self.sm)
        state.appcont = controller
        state.models = Models()
        state.detection = Detection()
        
        controller.load_initial_screen()
        return self.sm

if __name__=="__main__":
    CaltonDatx().run()