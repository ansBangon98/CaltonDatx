from kivy.uix.accordion import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.core.text import Label
from kivy.core.window import Window



class Caption():
    def _display_caption(self, object, text):
        # color=(1, 1, 1, 1)
        color=(0, 0, 0, 1)
        font_size=20
        x1, _, _, y2 = object['coords']
        resolution = object['resolution']
        widget = object['widget']
        size = widget.size
        win_size = Window.size
        x = x1 + (size[0]-resolution[0]) / 2
        y = ((resolution[1] - y2) + (size[1]-resolution[1]) / 2 ) + (win_size[1]-size[1]) + 5
        label = Label(text=text, font_size=font_size)
        label.refresh()
        texture = label.texture
        texture_size = texture.size

        with widget.canvas.after:
            Color(*color)  # RGBA
            Rectangle(texture=texture, pos=(x, y), size=texture_size)

class Track():
    def _create_body_box(self, object):
        x1, y1, x2, y2 = object['coords']
        resolution = object['resolution']
        widget = object['widget']
        size = widget.size
        win_size = Window.size
        with widget.canvas.after:
            x = x1 + (size[0]-resolution[0]) / 2
            y = ((resolution[1] - y2) + (size[1]-resolution[1]) / 2 ) + (win_size[1]-size[1]) + 5
            w = x2 - x1
            h = y2 - y1
            Color(0.3333, 0.0078, 0.9804)
            Line(rectangle=(x, y, w, h), width=1)

            Color(0, 1, 0)
            corner_len = min(w, h) * 0.15
            
            Line(points=[x, y + h, x + corner_len, y + h], width=2)
            Line(points=[x, y + h, x, y + h - corner_len], width=2)

            Line(points=[x + w, y + h, x + w - corner_len, y + h], width=2)
            Line(points=[x + w, y + h, x + w, y + h - corner_len], width=2)

            Line(points=[x, y, x + corner_len, y], width=2)
            Line(points=[x, y, x, y + corner_len], width=2)

            Line(points=[x + w, y, x + w - corner_len, y], width=2)
            Line(points=[x + w, y, x + w, y + corner_len], width=2)

    def _create_face_box(self, object):
        x1, y1, x2, y2 = object['coords']
        resolution = object['resolution']
        widget = object['widget']
        size = widget.size
        win_size = Window.size
        with widget.canvas.after:
            x = x1 + (size[0]-resolution[0]) / 2
            y = ((resolution[1] - y2) + (size[1]-resolution[1]) / 2 ) + (win_size[1]-size[1]) + 5
            w = x2 - x1
            h = y2 - y1

            Color(0, 1, 0)
            corner_len = min(w, h) * 0.15
            
            Line(points=[x, y + h, x + corner_len, y + h], width=1)
            Line(points=[x, y + h, x, y + h - corner_len], width=1)

            Line(points=[x + w, y + h, x + w - corner_len, y + h], width=1)
            Line(points=[x + w, y + h, x + w, y + h - corner_len], width=1)

            Line(points=[x, y, x + corner_len, y], width=1)
            Line(points=[x, y, x, y + corner_len], width=1)

            Line(points=[x + w, y, x + w - corner_len, y], width=1)
            Line(points=[x + w, y, x + w, y + corner_len], width=1)