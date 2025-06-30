import numpy as np

from kivy.uix.accordion import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.core.text import Label
from kivy.core.window import Window
from PIL import Image, ImageDraw, ImageFont



class Caption():
    def _display_caption(self, frame, coords, caption):
        x, y = coords
        x, y = x+5, y+5
        image = Image.fromarray(frame)
        image_draw = ImageDraw.Draw(image)

        color = (0, 0, 0)
        font = ImageFont.truetype('./assets/fonts/Roboto-Regular.ttf', 14)
        image_draw.text((x, y), caption, fill=color, font=font)
        return np.array(image)

class Track():
    def _create_body_box(self, frame, coords):
        x1, y1, x2, y2 = coords
        w = x2 - x1
        h = y2 - y1
        image = Image.fromarray(frame)
        image_draw = ImageDraw.Draw(image)

        color = (85, 2, 250)
        image_draw.rectangle([x1, y1, x2, y2], outline=color, width=1)

        color = (0, 255, 0)
        corner_len = int(min(w, h) * 0.15)
        image_draw.line([x1, y1, x1 + corner_len, y1], fill=color, width=5)
        image_draw.line([x1, y1, x1, y1 + corner_len], fill=color, width=5)

        image_draw.line([x2 - corner_len, y1, x2, y1], fill=color, width=5)
        image_draw.line([x2, y1, x2, y1 + corner_len], fill=color, width=5)

        image_draw.line([x1, y2, x1 + corner_len, y2], fill=color, width=5)
        image_draw.line([x1, y2, x1, y2 - corner_len], fill=color, width=5)

        image_draw.line([x2 - corner_len, y2, x2, y2], fill=color, width=5)
        image_draw.line([x2, y2, x2, y2 - corner_len], fill=color, width=5)
        return np.array(image)

    def _create_face_box(self, frame, coords):
        x1, y1, x2, y2 = coords
        w = x2 - x1
        h = y2 - y1
        image = Image.fromarray(frame)
        image_draw = ImageDraw.Draw(image)

        color = (0, 174, 255)
        corner_len = int(min(w, h) * 0.15)
        image_draw.line([x1, y1, x1 + corner_len, y1], fill=color, width=2)
        image_draw.line([x1, y1, x1, y1 + corner_len], fill=color, width=2)

        image_draw.line([x2 - corner_len, y1, x2, y1], fill=color, width=2)
        image_draw.line([x2, y1, x2, y1 + corner_len], fill=color, width=2)

        image_draw.line([x1, y2, x1 + corner_len, y2], fill=color, width=2)
        image_draw.line([x1, y2, x1, y2 - corner_len], fill=color, width=2)

        image_draw.line([x2 - corner_len, y2, x2, y2], fill=color, width=2)
        image_draw.line([x2, y2, x2, y2 - corner_len], fill=color, width=2)
        return np.array(image)