import numpy as np
import core.state as state

# import tensorflow as tf
from collections import deque, Counter
from PIL import Image

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / np.sum(e_x)

def __image_resize(image_array, size, channel):
    image = Image.fromarray(image_array).convert(channel)
    resize_image = image.resize(size, Image.LANCZOS)
    image_array = np.array(resize_image)
    return image_array
"""
def _3d_preprocess_image_quantize(image_array, input_scale, input_zero_point):
    # img = cv2.resize(image_array, (224, 224))
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    __image_resize(image_array)
    img = np.asarray(img, dtype=np.float32)

    # Normalize to original float32 range [0, 1]
    img = img / 255.0

    # Quantize to uint8
    img = img / input_scale + input_zero_point
    img = np.clip(img, 0, 255).astype(np.uint8)

    return np.expand_dims(img, axis=0)  # shape: (1, 224, 224, 3)
"""

def _3d_preprocess_image(image_array):
    img = __image_resize(image_array, (224, 224), 'RGB')
    img = np.asarray(img, dtype=np.float32)
    img = img / 255.0
    return np.expand_dims(img, axis=0)

def _1d_preprocess_image(image_array, input_scale, input_zero_point):
    img = __image_resize(image_array, (48, 48), 'L')
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)

    # Quantize
    img = img.astype(np.float32) / 255.0
    img = img / input_scale + input_zero_point
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img


class Age():
    def __init__(self):
        self.interpreter = state.models.age_interpreter
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_scale, self.input_zero_point = self.input_details[0]['quantization']
        self.output_scale, self.output_zero_point = self.output_details[0]['quantization']
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
        # image_tensor = _3d_preprocess_image_quantize(face, self.input_scale, self.input_zero_point)
        self.interpreter.set_tensor(self.input_details[0]['index'], image_tensor)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        # probabilities = tf.nn.softmax(output_data[0]).numpy()
        probabilities = softmax(output_data[0])
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
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_scale, self.input_zero_point = self.input_details[0]['quantization']
        self.output_scale, self.output_zero_point = self.output_details[0]['quantization']
        self.gender_list = {}
    
    def _predic_gender(self, face, id):
        image_tensor = _3d_preprocess_image(face)
        # image_tensor = _3d_preprocess_image_quantize(face, self.input_scale, self.input_zero_point)
        # print(image_tensor.shape)
        self.interpreter.set_tensor(self.input_details[0]['index'], image_tensor)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        # output_float = (output_data.astype(np.float32) - self.output_zero_point) * self.output_scale
        probabilities = softmax(output_data[0])
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
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_scale, self.input_zero_point = self.input_details[0]['quantization']
        self.output_scale, self.output_zero_point = self.output_details[0]['quantization']
        self.emotions = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    def _predic_emotion(self, face, id):
        image_tensor = _1d_preprocess_image(face, self.input_scale, self.input_zero_point)
        self.interpreter.set_tensor(self.input_details[0]['index'], image_tensor)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        output_float = (output_data.astype(np.float32) - self.output_zero_point) * self.output_scale
        probabilities = softmax(output_float[0])
        pred_class = np.argmax(probabilities)
        # conf = probabilities[pred_class]
        # if conf >= 0.5:
        return self.emotions[pred_class]
        # return None