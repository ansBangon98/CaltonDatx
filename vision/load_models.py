import os
import onnxruntime as ort
import tensorflow as tf
import tools.decrypt_model as decryptor
import tools.key_generator as keygen
import core.state as state

class Models():
    def __init__(self):
        # self.facpep_model = self.load_face_people()
        self.facpep_interpreter, self.facpep_input_details, self.facpep_output_details = self.load_face_people()

    def load_face_people(self):
        model_encrypted = "./models/face_people.bin"
        # model_encrypted = "./models/face_people.bin"
        if os.path.exists(model_encrypted):
            # model_path = decryptor.decrypt_model(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            # model = ort.InferenceSession(model_path.name, providers=["CPUExecutionProvider"], provider_options=[{"num_threads": 4}])
            # os.remove(model_path.name)
            # return model

            tflite_model_path = decryptor.decrypt_model(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            return interpreter, input_details, output_details
            