import core.state as state

from PIL import Image
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from ui.screens.deviceconfig import DeviceConfig

if platform == 'android':
    from jnius import autoclass
else:
    import cv2
    from pygrabber.dshow_graph import FilterGraph

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
            self.cam_bg = self.capture_background()
            self.ids = None

            self.camera = state.camera
            self.detection = state.detection

            self._prediction = []
            self._ageclassification =[]
            self.sm = screen_manager
            self.__cam_event = None
    
    def __load_camdevice_name(self):
        camdevice_name = ['Select an option']
        if platform == "android":
            Camera = autoclass('android.hardware.Camera')
            num_cameras = Camera.getNumberOfCameras()
            list_name = [f'Camera {i}' for i in range(1, num_cameras)]
        else:
            graph = FilterGraph()
            devices = graph.get_input_devices()
            list_name = [f"Camera {i+1} : {device}" for i, device in enumerate(devices)]
        
        camdevice_name.extend(list_name)
        self.ids.drp_cameras.values = camdevice_name
        self.ids.drp_cameras.text = "Select an option"
    
    def __load_resolutions(self, cam_index):
        resolution_list = ['Select an option']
        if platform == "android":
            Camera = autoclass('android.hardware.Camera')
            camera = Camera.open(cam_index)
            params = camera.getParameters()
            sizes = params.getSupportedPreviewSizes()
            camera.release()
            for i in range(sizes.size()):
                size = sizes.get(i)
                resolution_list.append(f'{size.width} x {size.height} {"(Recommended)" if i==0 else ""}')
        else:
            common_resolutions = [
                (1920, 1080),
                (1600, 1200),
                (1280, 720),
                (1024, 768),
                (800, 600),
                (640, 480),
                (320, 240)
            ]
            cap = cv2.VideoCapture(0)
            for (w, h) in common_resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                
                # Give time for settings to apply (may be needed in real apps)
                actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if (actual_w, actual_h) == (w, h):
                    resolution_list.append(f'{actual_w} x {actual_h} {"(Recommended)" if i==0 else ""}')
                    

            cap.release()

    def capture_background(self):
        image = Image.open("./assets/deviceconfig/cam_bg.png").convert('RGB')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        buf = image.tobytes()
        image_texture = Texture.create(size=image.size, colorfmt='rgb')
        image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        return image_texture
    
    def _load_initial_screen(self):
        deviceconfig = DeviceConfig(name ="device_config")
        self.sm.add_widget(deviceconfig)
        self.sm.title = "Device Configuration"
        self.sm.current = "device_config"
        self.ids = deviceconfig.ids
        self.ids.img_camera.texture = self.cam_bg

        self.__load_camdevice_name()

    def _get_webcam_image(self, dt):
        if self.camera._image is not None:
            self.ids.img_camera.texture = self.camera._image
    
    def _start_stop_camera(self):
        Window.set_system_cursor('wait')
        instance = self.ids.btn_start
        if instance.text == 'Start':
            instance.text = 'Stop'    
            self.camera._start_camera(0)
            self.__cam_event = Clock.schedule_interval(self._get_webcam_image, 1.0/30)
        else:
            instance.text = 'Start'
            self.camera._stop_camera()
            self.__cam_event.cancel()
            self.ids.img_camera.texture = self.cam_bg
        Window.set_system_cursor('arrow')

    def _validate_input_data(self):
        opt_camselected = 'network' if self.ids.opt_network.state == 'down' else 'camera' if self.ids.opt_camera.state == 'down' else None
        if opt_camselected is None:
            return False, 'Please select the device camera.'
        elif opt_camselected == 'network' and self.ids.txt_rtsp.text == '':
            return False, 'Please enter the RTSP/Link CCTV address.'
        elif opt_camselected == 'camera' and self.ids.drp_cameras.text == 'Select an option':
            return False, 'Please select the camera.'
        elif self.ids.drp_resolution.text == 'Select an option':
            return False, 'Please select the display resolution.'
        elif self.ids.drp_orientation.text == 'Select an option':
            return False, 'Please select the view orientation.'
        elif not self.detection._detection:
            return False, 'Please select the analytic detection.'
        # elif not self._prediction:
        #     return False, 'Please select the analytic prediction.'
        # elif not self._ageclassification:
        #     return False, 'Please select the analytic age classification.'
        else:
            return True, None