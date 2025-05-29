import os
import sys
import time
import api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime as dttime

class DataUploader():
    def __init__(self):
        self.base_directory = os.path.join(os.getenv("PROGRAMDATA"), "CaltonDatx", "data")
        self.__files_checker()
        self.apis = api()

    def __files_checker(self):
        while(True):
            curr_filename = f'{dttime.now().strftime("%m-%d-%y %H%M")}.txt'
            file_list = [os.path.join(self.base_directory, file) for file in os.listdir(self.base_directory) if file.endswith('.txt') and file != curr_filename]
            if file_list:
                for file in file_list:
                    filename = os.path.basename(file)
                    with open(file, 'rb') as file:
                        file_data = {'file':(filename, file.read())}
                        self.apis._file_uploader(filename, file_data)

if __name__=="__main__":
    DataUploader()