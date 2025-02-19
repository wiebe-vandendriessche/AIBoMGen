import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
import joblib

# Load MNIST dataset from openml
mnist = fetch_openml('mnist_784', version=1)

# Prepare the data
X = mnist.data / 255.0  # Normalize the data
y = mnist.target.astype(int)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the Random Forest Classifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {accuracy:.4f}")

# Save the trained model
output_model_path = "/output/model2.joblib"
joblib.dump(model, output_model_path)

print(f"Model saved to {output_model_path}")
