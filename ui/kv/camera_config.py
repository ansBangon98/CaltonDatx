from kivy.uix.effectwidget import Rectangle
from kivy.uix.behaviors.touchripple import Color
import os
import sys

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock

# Window.clearcolor = (1, 1, 1, 1)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

kv_file = resource_path("ui/kv/camera_settings.kv")
Builder.load_file(kv_file)
class CameraSettings(BoxLayout):
    pass

kv_file = resource_path("ui/kv/detection.kv")
Builder.load_file(kv_file)
class Detection(BoxLayout):
    pass

kv_file = resource_path("ui/kv/prediction.kv")
Builder.load_file(kv_file)
class Prediction(BoxLayout):
    pass


kv_file = resource_path("ui/kv/camera_configuration.kv")
Builder.load_file(kv_file)

class CameraConfiguration(Screen):
    panel_visible = False
    current_panel = None
    nav_selected = None

    def __init__(self, **kw):
        super().__init__(**kw)
        # Window.bind(on_resize=self.on_window_resize)
        # self.ids.display_content.add_widget(CameraSettings())
    
    def on_window_resize(self, window, width, height):
        if self.check_screen_size():
            self.ids.content_layout1.orientation = 'vertical'
        else:
            self.ids.content_layout1.orientation = 'horizontal'
    
    def check_screen_size(self):
        width, height = Window.size
        dpi = Window.dpi or 160
        diagonal = ((width / dpi) ** 2 + (height / dpi) ** 2) ** 0.5

        if diagonal <= 7.0:
            return True
            # print(f"Mobile Phone Size Detected\n{Window.size}, {dpi:.1f} dpi")
        else:
            return False
            # print(f"Not a Mobile Phone\n{Window.size}, {dpi:.1f} dpi")
    
    def toggle_panel(self, screen_name, instance):
        panel = self.ids.side_panel
        panel_container = self.ids.panel_container

        def clear_canvas():
            if self.nav_selected is not None:
                self.nav_selected.canvas.clear()

        def show_panel(*args):
            panel_container.clear_widgets()
            if screen_name == 'camsettings':
                panel_container.add_widget(CameraSettings())
                self.nav_selected = instance.parent
                with self.nav_selected.canvas.before:
                    Color(0.1373, 0.1373, 0.1373, 1)
                    Rectangle(size=self.nav_selected.size, pos=self.nav_selected.pos)
            elif screen_name == 'detection':
                panel_container.add_widget(Detection())
            elif screen_name == 'prediction':
                panel_container.add_widget(Prediction())

            Animation(x=0, duration=0.3).start(panel)
            self.current_panel = screen_name
            self.panel_visible = True
        clear_canvas()
        if self.panel_visible:
            if self.current_panel == screen_name:
                Animation(x=-panel.width, duration=0.3).start(panel)
                self.panel_visible = False
                self.current_panel = None
            else:
                anim = Animation(x=-panel.width, duration=0.3)
                anim.bind(on_complete=lambda *args: Clock.schedule_once(show_panel, 0.05))
                anim.start(panel)
        else:
            show_panel()
    

class CamApp(App):
    def build(self):
        sm = ScreenManager()
        camconfig = CameraConfiguration(name="cam_configuration")
        sm.add_widget(camconfig)
        sm.title = "Camera Configuration"
        return sm

if __name__ == "__main__":
    CamApp().run()
