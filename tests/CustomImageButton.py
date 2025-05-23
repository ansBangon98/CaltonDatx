from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.animation import Animation


# Load KV layout from string
KV = """
<ImageButton>:
    fit_mode: 'contain'
    size_hint: None, None
    size: 40, 40

BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10

    ImageButton:
        source: './assets/deviceconfig/capture.png'
        on_press: app.capture_pressed()
"""

# Create a button-like image class
class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        Animation(size=(36, 36), d=0.1).start(self)

    def on_release(self):
        Animation(size=(40, 40), d=0.1).start(self)
    # pass

# Main app class
class MyApp(App):
    def build(self):
        return Builder.load_string(KV)

    def capture_pressed(self):
        print("Capture image clicked!")

if __name__ == '__main__':
    MyApp().run()
