from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.properties import StringProperty, NumericProperty

class TextCanvasWidget(Widget):
    text = StringProperty("Hello, Kivy!")  # Allows text updates from KV
    font_size = NumericProperty(24)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.update_canvas, font_size=self.update_canvas)  # Update when properties change
        self.update_canvas()

    def update_canvas(self, *args):
        """Clears and redraws the text on the canvas."""
        self.canvas.clear()

        # Create CoreLabel to render text
        core_label = CoreLabel(text=self.text, font_size=self.font_size)
        core_label.refresh()  # Generate texture

        texture = core_label.texture
        texture_size = texture.size

        with self.canvas:
            Color(0, 0, 0, 1)  # Black text color
            Rectangle(texture=texture, pos=self.pos, size=texture_size)
