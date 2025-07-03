from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner

class MyWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner = Spinner(
            text='Select an option',
            values=('Apple', 'Banana', 'Cherry', 'Date'),
            size_hint=(None, None),
            size=(150, 44),
            pos_hint={'center_x': .5, 'center_y': .5})
        self.spinner.bind(text=self.on_spinner_select)
        self.add_widget(self.spinner)

    def on_spinner_select(self, spinner, text):
        index = spinner.values.index(text)
        print(f'Selected value: {text}, Index: {index}')

class MyApp(App):
    def build(self):
        return MyWidget()

MyApp().run()
