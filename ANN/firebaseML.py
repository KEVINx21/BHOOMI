import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

# Load and preprocess data
data = pd.read_csv('crop_recommendation.csv')

X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label'] 

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define the Fully Connected Neural Network (FCNN) model
model = Sequential([
    Dense(64, input_shape=(7,), activation='relu'),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dense(y_categorical.shape[1], activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.2, verbose=1)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
test_accuracy = test_accuracy * 100
print(f'Test Accuracy: {test_accuracy:.2f}%')

# Export the model to TensorFlow Lite format
def export_to_tflite(model, filename="crop_recommendation_model.tflite"):
    # Convert the Keras model to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    
    # Save the TFLite model to a file
    with open(filename, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite model saved as {filename}")

# Call the function to export
export_to_tflite(model)

# Function to simulate user input
def get_user_input():
    print("Enter the following values to predict the crop:")
    
    N = float(input("Enter Nitrogen (N) value: "))
    P = float(input("Enter Phosphorus (P) value: "))
    K = float(input("Enter Potassium (K) value: "))
    temperature = float(input("Enter Temperature (°C): "))
    humidity = float(input("Enter Humidity (%): "))
    ph = float(input("Enter PH value: "))
    rainfall = float(input("Enter Rainfall (mm): "))
    
    return np.array([N, P, K, temperature, humidity, ph, rainfall]).reshape(1, -1)

# Normalize user input before passing to the model
user_input = get_user_input()
user_input_scaled = scaler.transform(user_input)

# Make a prediction using the trained model
prediction = model.predict(user_input_scaled)
predicted_class = np.argmax(prediction, axis=1)

# Map the predicted class back to the crop label
predicted_crop = label_encoder.inverse_transform(predicted_class)

# Display the predicted crop
print(f"The predicted crop is: {predicted_crop[0]}")
