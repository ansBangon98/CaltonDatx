from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.properties import StringProperty, NumericProperty

class TextCanvasWidget(Widget):
    text = StringProperty("Hello, Ans!")
    font_size = NumericProperty(24)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.update_canvas, font_size=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()

        core_label = CoreLabel(text=self.text, font_size=self.font_size)
        core_label.refresh()

        texture = core_label.texture
        texture_size = texture.size

        with self.canvas:
            Color(0, 0, 0, 1)
            Rectangle(texture=texture, pos=self.pos, size=texture_size)
