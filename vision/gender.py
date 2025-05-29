import numpy as np
import tensorflow as tf
import core.state as state
import cv2

from PIL import Image

class Gender():
    def __init__(self):
        self.interpreter = state.models.gender_interpreter
        self.input = state.models.gender_input_details
        self.output = state.models.gender_output_details
    
    def __preprocess_image(self, image_array):
        # img_size = (224, 224)
        # mean = tf.constant([0.485, 0.456, 0.406])
        # std = tf.constant([0.229, 0.224, 0.225])

        # img = Image.fromarray(image_array).convert("RGB").resize(img_size)
        # img = np.array(img) / 255.0
        # img = (img - mean.numpy()) / std.numpy()
        # img = np.expand_dims(img, axis=0).astype(np.float32)
        # return tf.convert_to_tensor(img)
        # Resize
        
        img = cv2.resize(image_array, (224, 224))

        # Convert BGR (OpenCV) to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Normalize to [0, 1]
        img = img.astype(np.float32) / 255.0

        # Apply normalization (same as PyTorch: mean and std)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = (img - mean) / std  # Shape: (224, 224, 3)

        # Transpose to (3, 224, 224) for channel-first
        img = np.transpose(img, (2, 0, 1))

        # Add batch dimension → (1, 3, 224, 224)
        input_tensor = np.expand_dims(img, axis=0).astype(np.float32)
        return input_tensor

    def _predic_gender(self, face):
        image_tensor = self.__preprocess_image(face)
        self.interpreter.set_tensor(self.input[0]['index'], image_tensor)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output[0]['index'])
        probabilities = tf.nn.softmax(output[0]).numpy()
        pred_class = np.argmax(probabilities)
        conf = probabilities[pred_class]
        if conf >= 0.5:
            return 'Male' if pred_class == 0 else 'Female'
        return None