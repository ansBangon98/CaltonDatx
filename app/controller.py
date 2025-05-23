from ui.screens.deviceconfig import DeviceConfig
import core.state as state

class AppController():
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__is_initialized = False
        return cls.__instance
            
    def __init__(self, screen_manager):
        if not self.__is_initialized:
            self.__is_initialized = True
            self.camera = state.camera
            self._detection = ['Face', 'Body']
            self._prediction = []
            self._ageclassification =[]
            self.sm = screen_manager

    def load_initial_screen(self):
        deviceconfig = DeviceConfig(name ="device_config")
        self.sm.add_widget(deviceconfig)
        self.sm.title = "Device Configuration"
        self.sm.current = "device_config"