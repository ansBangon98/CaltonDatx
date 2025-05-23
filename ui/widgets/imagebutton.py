from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation

class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        Animation(size=(36, 36), d=0.1).start(self)

    def on_release(self):
        Animation(size=(40, 40), d=0.1).start(self)