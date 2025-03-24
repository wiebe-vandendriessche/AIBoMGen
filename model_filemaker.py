import tensorflow as tf
from tensorflow.keras import layers, models
import tf2onnx

# Define the model
model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)),  # Input layer for 28x28 images (like MNIST)
    layers.Dense(128, activation='relu'),  # Hidden layer with ReLU activation
    layers.Dropout(0.2),  # Dropout layer for regularization
    layers.Dense(10)  # Output layer with 10 units (for classification)
])

# Compile the model
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# Define the output directory for saving the models
output_model_path = "C:/Users/wiebe/Downloads/"

# Save the model in different formats

# Save in the older Keras `.h5` format
model.save(output_model_path + "model.h5")

# Save in the new Keras `.keras` format
model.save(output_model_path + "model.keras")

# Save the model in TensorFlow's SavedModel format
tf.saved_model.save(model, output_model_path + "saved_model")

# Save in TensorFlow Lite `.tflite` format (optimized for mobile and embedded devices)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
with open(output_model_path + "model.tflite", "wb") as f:
    f.write(tflite_model)

# Save in ONNX format
onnx_model = tf2onnx.convert.from_keras(model)
onnx_model.save(output_model_path + "model.onnx")

# Save for TensorFlow.js in `.json` format
import tensorflowjs as tfjs
tfjs.converters.save_keras_model(model, output_model_path + "model_js")

# Optional: Save model for TensorFlow Hub in `.tar` format
import tensorflow_hub as hub
model_for_hub = hub.KerasLayer(model)
model_for_hub.save(output_model_path + "model_for_hub")