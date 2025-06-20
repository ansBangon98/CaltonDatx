import os
import onnxruntime as ort
import tensorflow as tf
import tools.decryptor as decrypt
import tools.key_generator as keygen
import core.state as state

class Models():
    def __init__(self):
        self.age_interpreter = self.load_age()
        self.gender_interpreter = self.load_gender()
        self.emotion_interpreter = self.load_emotion()
        self.facpep_interpreter = self.load_face_people()

    def load_face_people(self):
        model_encrypted = "./models/face_people.tflite"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key),'.tflite')
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()
            """
            # input_details = interpreter.get_input_details()
            # output_details = interpreter.get_output_details()
            # print(f"detection input type: {input_details}")
            # print(f"detection output type: {output_details}")
            """
            return interpreter #, input_details, output_details
    
    def load_gender(self):
        model_encrypted = "./models/gender.bin" #MOBILENETv3-small
        # model_encrypted = "./models/mobilenet_v3_small_gender.bin"
        # model_encrypted = "./models/mobilenet_v3_small_gender_quantized.bin"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key), '.tflite')
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()
            """
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(f"gender input: \n{input_details}")
            print(f"gender output: \n{output_details}")
            """
            return interpreter #, input_details, output_details
    
    def load_age(self):
        model_encrypted = "./models/age.bin"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key), '.tflite')
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()
            """
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(f"age input: \n{input_details}")
            print(f"age output: \n{output_details}")
            """
            return interpreter #, input_details, output_details
    
    def load_emotion(self):
        model_encrypted = "./models/emotion.bin"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key), '.tflite')
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()
            """
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(f"emotion input: \n{input_details}")
            print(f"emotion output: \n{output_details}")
            """
            return interpreter #, input_details, output_details
            