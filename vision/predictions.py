import numpy as np
import tensorflow as tf
import core.state as state
import cv2

from keras.preprocessing.image import img_to_array
from collections import deque, Counter

from PIL import Image

def _3d_preprocess_image(image_array):
    size = (224, 224)
    mean = tf.constant([0.485, 0.456, 0.406])
    std = tf.constant([0.229, 0.224, 0.225])

    img = Image.fromarray(image_array).convert("RGB").resize(size)
    img = np.array(img) / 255.0
    img = (img - mean.numpy()) / std.numpy()
    img = np.expand_dims(img, axis=0).astype(np.float32)
    return img

def _1d_preprocess_image(image_array):
    size = (48, 48)
    img = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    img = img.astype(float) / 255.0
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    return img

    # mean = tf.constant([0.5])
    # std = tf.constant([0.5])

    # img = Image.fromarray(image_array).convert("L").resize(size)
    # img = np.array(img) / 255.0
    # img = (img - mean.numpy()) / std.numpy()
    # img = np.expand_dims(img, axis=-1)
    # img = np.expand_dims(img, axis=0)

    # return img.astype(np.float32)

class Age():
    def __init__(self):
        self.interpreter = state.models.age_interpreter
        self.input = state.models.age_input_details
        self.output = state.models.age_output_details
        self.age_list = {}
    
    def __get_age_category(self, age_index):
        age_classification = "Young Adult"
        if age_index == 0:
            age_classification = "Child"
        elif age_index == 1:
            age_classification = "Teen"
        elif age_index == 2:
            age_classification = "Young Adult"
        elif age_index == 3:
            age_classification = "Adult"
        elif age_index >= 4 and age_index <= 5:
            age_classification = "Middle Age"
        elif age_index > 5:
            age_classification = "Senior"
        return age_classification

    def _predic_age(self, face, id):
        image_tensor = _3d_preprocess_image(face)
        self.interpreter.set_tensor(self.input[0]['index'], image_tensor)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output[0]['index'])
        probabilities = tf.nn.softmax(output[0]).numpy()
        pred_class = np.argmax(probabilities)
        conf = probabilities[pred_class]
        if conf >= 0.5:
            age_group = self.__get_age_category(pred_class)
            if id not in self.age_list:
                self.age_list[id] = deque([age_group], maxlen=20)
            else:
                self.age_list[id].append(age_group)
        if id in self.age_list:
            return Counter(self.age_list[id]).most_common(1)[0][0]
        return None

class Gender():
    def __init__(self):
        self.interpreter = state.models.gender_interpreter
        self.input = state.models.gender_input_details
        self.output = state.models.gender_output_details
        self.gender_list = {}
    

    def _predic_gender(self, face, id):
        image_tensor = _3d_preprocess_image(face)
        self.interpreter.set_tensor(self.input[0]['index'], image_tensor)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output[0]['index'])
        probabilities = tf.nn.softmax(output[0]).numpy()
        pred_class = np.argmax(probabilities)
        conf = probabilities[pred_class]
        if conf >= 0.5:
            gender = 'Male' if pred_class == 0 else 'Female'
            if id not in self.gender_list:
                self.gender_list[id] = deque([gender], maxlen=20)
            else:
                self.gender_list[id].append(gender)
        if id in self.gender_list:
            return Counter(self.gender_list[id]).most_common(1)[0][0]
        return None
    
class Emotion():
    def __init__(self):
        self.interpreter = state.models.emotion_interpreter
        self.input = state.models.emotion_input_details
        self.output = state.models.emotion_output_details
        self.emotions = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    def _predic_emotion(self, face, id):
        image_tensor = _1d_preprocess_image(face)
        self.interpreter.set_tensor(self.input[0]['index'], image_tensor)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output[0]['index'])
        probabilities = tf.nn.softmax(output[0]).numpy()
        pred_class = np.argmax(probabilities)
        # conf = probabilities[pred_class]
        # if conf >= 0.5:
        return self.emotions[pred_class]
        # return None