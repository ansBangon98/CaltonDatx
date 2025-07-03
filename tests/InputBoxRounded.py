from kivy.uix.textinput import TextInput
from kivy.lang import Builder

Builder.load_string("""
<RoundedTextInput@TextInput>:
    background_normal: ""
    background_active: ""
    background_color: 0, 0, 0, 0
    foreground_color: 0, 0, 0, 1
    padding: 10
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
""")
