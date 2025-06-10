import os
import onnxruntime as ort
import tensorflow as tf
import tools.decryptor as decrypt
import tools.key_generator as keygen
import core.state as state

class Models():
    def __init__(self):
        self.age_interpreter, self.age_input_details, self.age_output_details = self.load_age()
        self.gender_interpreter, self.gender_input_details, self.gender_output_details = self.load_gender()
        self.emotion_interpreter, self.emotion_input_details, self.emotion_output_details = self.load_emotion()
        self.facpep_interpreter, self.facpep_input_details, self.facpep_output_details = self.load_face_people()

    def load_face_people(self):
        model_encrypted = "./models/face_people.tflite"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            # print(f'input: {input_details}')
            # print()
            # print()
            # print(f'output: {output_details}')

            return interpreter, input_details, output_details
    
    def load_gender(self):
        model_encrypted = "./models/gender.tflite"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            # print(f'gender input: {input_details}')
            # print()
            # print()
            # print(f'gender output: {output_details}')
            return interpreter, input_details, output_details
    
    def load_age(self):
        model_encrypted = "./models/age.tflite"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            # print(f'age input: {input_details}')
            # print()
            # print()
            # print(f'age output: {output_details}')
            return interpreter, input_details, output_details
    
    def load_emotion(self):
        model_encrypted = "./models/emotion.tflite"
        if os.path.exists(model_encrypted):
            tflite_model_path = decrypt.decrypt(model_encrypted, keygen.generate_32byte_key(state.encryption_key))
            interpreter = tf.lite.Interpreter(model_path=tflite_model_path.name)
            os.remove(tflite_model_path.name)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            # print(f'emotion input: {input_details}')
            # print()
            # print()
            # print(f'emotion output: {output_details}')
            return interpreter, input_details, output_details
            