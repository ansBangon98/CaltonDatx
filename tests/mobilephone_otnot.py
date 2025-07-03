from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.clock import Clock

class MainApp(App):
    def build(self):
        self.label = Label(text="Checking screen size...")
        # Initial check
        Clock.schedule_once(lambda dt: self.check_screen_size(), 0)
        # Bind resize event
        Window.bind(on_resize=self.on_window_resize)
        return self.label

    def on_window_resize(self, window, width, height):
        self.check_screen_size()

    def check_screen_size(self):
        width, height = Window.size
        dpi = Window.dpi or 160  # fallback if dpi is 0
        diagonal = ((width / dpi) ** 2 + (height / dpi) ** 2) ** 0.5

        if diagonal <= 7.0:
            self.label.text = f"Mobile Phone Size Detected\n{Window.size}, {dpi:.1f} dpi"
        else:
            self.label.text = f"Not a Mobile Phone\n{Window.size}, {dpi:.1f} dpi"

if __name__ == "__main__":
    MainApp().run()
