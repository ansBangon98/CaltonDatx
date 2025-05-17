import os
import sys
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import StringProperty
from kivy.uix.popup import Popup

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ShowMessage_Info(Popup):
    message_text = StringProperty()

class ShowMessage_Ask(Popup):
    message_text = StringProperty()

# class MessageBox_Info():
#     def Show(title='', message_text=''):
#         ShowMessage_Ask = Factory.ShowMessage_Ask(title, message_text)
#         ShowMessage_Ask.open()


Factory.register('ShowMessage_Info', cls=ShowMessage_Info)
Factory.register('ShowMessage_Ask', cls=ShowMessage_Ask)

popup_FILE = resource_path("ui/widgets/popup.kv")
Builder.load_file(popup_FILE)
