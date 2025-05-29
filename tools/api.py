import os
import sys
import requests
import decryptor as decrypt
import key_generator as keygen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import core.state as state

from core.logs import Logs


class API():
    def __init__(self):
        self.logs = Logs()

        self.url = None
        self.api_key = None

    def __load_apis(self):
        api_dir = './data/api.ini'
        api_temp_dir = decrypt.decrypt(api_dir, keygen.generate_32byte_key(state.encryption_key))
        details = None
        with open(api_temp_dir.name, 'r') as file:
            details = file.readlines()
        os.remove(api_temp_dir.name)

    def _file_uploader(self, filename, filedata):
        try:
            header = {
                "api-key": self.api_key
            }
            file = {
                'file' : (filename, filedata)
            }
            response = requests.post(self.url, headers=header, files=file)
            if response.status_code != 201:
                self.logs._insert_logs(f"Failed to upload image: {response.status_code}")
            else:
                self.logs._insert_logs(f'Device: {self.config.device_serial_number} request live preview | status : {str(response.status_code)}.')
        except requests.exceptions.ConnectionError:
            self.logs._insert_logs("No internet connection. Unable to send the GET request.")
        except requests.exceptions.RequestException as e:
            self.logs._insert_logs(f'An error occurred: {e}')

if __name__=="__main__":
    API()