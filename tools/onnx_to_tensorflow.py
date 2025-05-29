import os
import onnx

from onnx_tf.backend import prepare

# Load the ONNX model
onnx_model = onnx.load(onnx_model_path)

# Prepare the ONNX model for TensorFlow backend
tf_rep = prepare(onnx_model)

# Define the TensorFlow SavedModel directory
tensorflow_path = os.path.join(tempdir, f'{model_name}_TensorFlow')

# Export the TensorFlow SavedModel
tf_rep.export_graph(tensorflow_path)

print(f"ONNX model converted to TensorFlow SavedModel at: {tensorflow_path}")