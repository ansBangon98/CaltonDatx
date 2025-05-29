import os

from datetime import datetime as dttime

class Logs():
    def __init__(self):
        self.base_directory = os.path.join(os.getenv('PROGRAMDATA'), 'CaltonDatx', 'Logs', 'Services')
        self.today_log_filename = f"Logs Services {dttime.now().strftime('%m%d%Y')}.txt"
        os.makedirs(self.base_directory, exist_ok=True)

        self.__clear_past_logs()
        self.__create_logs()
    
    def __clear_past_logs(self):
        curr_filename = self.today_log_filename[:16]
        file_names = [os.path.join(self.base_directory, file) for file in os.listdir(self.base_directory) if not file.startswith(curr_filename)]
        for file_path in file_names:
            if os.path.exists(file_path):
                os.remove(file_path)

    def __create_logs(self):
        logs_file_directory = os.path.join(self.base_directory, self.today_log_filename)
        with open(logs_file_directory, 'a') as file:
            file.write(f'LOGS DATE: {dttime.now().strftime("%m-%d-%Y")}\nStarting logs. . . \n')

    def _insert_logs(self, description):
        logs_file_directory = os.path.join(self.base_directory, self.today_log_filename)
        with open(logs_file_directory, 'a') as file:
            file.write(f'{dttime.now().strftime("%m-%d-%Y %I:%M:%S %p")} | {description}')