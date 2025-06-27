import os
import tools.decryptor as decrypt
import tools.key_generator as keygen
import core.state as state
import uuid

from kivy.utils import platform
from kivy.resources import resource_find
from kivy.utils import platform

if platform == 'android':
    import tflite_runtime.interpreter as tflite
    from android.storage import app
    # shared_storage_path = "/storage/emulated/0/CaltonDatx"
    shared_storage_path = app().get_cache_dir()
    if not os.path.exists(shared_storage_path):
        os.makedirs(shared_storage_path)
    tmp_dir = shared_storage_path
else:
    import tensorflow as tf
    tflite = tf.lite

    import tempfile
    tmp_dir = tempfile.gettempdir()

if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir, exist_ok=True)

class Models():
    def __init__(self):
        self.facpep_interpreter = self.load_face_people()
        self.age_interpreter = self.load_age()
        self.gender_interpreter = self.load_gender()
        self.emotion_interpreter = self.load_emotion()

    def load_face_people(self):
        model_encrypted = resource_find("models/face_people.bin")
        if os.path.exists(model_encrypted):
            temp_filename = f'{str(uuid.uuid4())}.tflite'
            decrypted_path = os.path.join(tmp_dir, temp_filename)
            decrypt.decrypt(
                model_encrypted,
                keygen.generate_32byte_key(state.encryption_key), 
                output_path=decrypted_path
                )
            interpreter = tflite.Interpreter(model_path=decrypted_path)
            interpreter.allocate_tensors()
            os.remove(decrypted_path)
            return interpreter
    
    def load_gender(self):
        model_encrypted = "./models/gender.bin"
        if os.path.exists(model_encrypted):
            temp_filename = f'{str(uuid.uuid4())}.tflite'
            decrypted_path = os.path.join(tmp_dir, temp_filename)
            decrypt.decrypt(
                model_encrypted,
                keygen.generate_32byte_key(state.encryption_key), 
                output_path=decrypted_path
                )
            interpreter = tflite.Interpreter(model_path=decrypted_path)
            interpreter.allocate_tensors()
            os.remove(decrypted_path)
            return interpreter
    
    def load_age(self):
        model_encrypted = "./models/age.bin"
        if os.path.exists(model_encrypted):
            temp_filename = f'{str(uuid.uuid4())}.tflite'
            decrypted_path = os.path.join(tmp_dir, temp_filename)
            decrypt.decrypt(
                model_encrypted,
                keygen.generate_32byte_key(state.encryption_key), 
                output_path=decrypted_path
                )
            interpreter = tflite.Interpreter(model_path=decrypted_path)
            interpreter.allocate_tensors()
            os.remove(decrypted_path)
            return interpreter
    
    def load_emotion(self):
        model_encrypted = "./models/emotion.bin"
        if os.path.exists(model_encrypted):
            temp_filename = f'{str(uuid.uuid4())}.tflite'
            decrypted_path = os.path.join(tmp_dir, temp_filename)
            decrypt.decrypt(
                model_encrypted,
                keygen.generate_32byte_key(state.encryption_key), 
                output_path=decrypted_path
                )
            interpreter = tflite.Interpreter(model_path=decrypted_path)
            interpreter.allocate_tensors()
            # print(f'Input details : {interpreter.get_input_details()}\n\n')
            # print(f'Output details : {interpreter.get_output_details()}\n\n')
            os.remove(decrypted_path)
            return interpreter
            