from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        return MyLayout()

class MyLayout(BoxLayout):
    pass

if __name__ == '__main__':
    MyApp().run()
