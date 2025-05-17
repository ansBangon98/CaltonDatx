from ui.screens.deviceconfig import DeviceConfig

class AppController():
    def __init__(self, screen_manager):
        self.sm = screen_manager

    def load_initial_screen(self):
        deviceconfig = DeviceConfig(name ="device_config")
        self.sm.add_widget(deviceconfig)
        self.sm.title = "Device Configuration"
        self.sm.current = "device_config"