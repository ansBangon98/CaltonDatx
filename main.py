from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from app.controller import AppController

class CaltonDatx(App):
    def build(self):
        self.sm = ScreenManager()
        controller = AppController(screen_manager=self.sm)
        controller.load_initial_screen()
        return self.sm

if __name__=="__main__":
    CaltonDatx().run()