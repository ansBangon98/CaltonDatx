from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.clock import Clock

class CameraView(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Kivy Camera widget
        self.camera = Camera(resolution=(640, 480), play=True)
        self.add_widget(self.camera)

class CameraApp(App):
    def build(self):
        return CameraView()

if __name__ == '__main__':
    CameraApp().run()
