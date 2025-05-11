import serial
import time
import numpy as np
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# Connect to the Arduino serial port
ser = serial.Serial('COM13', 115200)  # Update 'COM13' with your Arduino's COM port
time.sleep(2)  # Wait for serial connection to initialize

def get_sensor_data():
    """Reads and extracts sensor data from Arduino over serial in labeled format."""
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()  # Read a line from the serial port
        
        # Use regex to match each sensor's value
        moisture_match = re.search(r"Moisture:\s*([\d.]+)", line)
        temperature_match = re.search(r"Temperature:\s*([\d.]+)", line)
        ec_match = re.search(r"EC:\s*([\d.]+)", line)
        ph_match = re.search(r"pH:\s*([\d.]+)", line)
        nitrogen_match = re.search(r"Nitrogen:\s*([\d.]+)", line)
        phosphorous_match = re.search(r"Phosphorous:\s*([\d.]+)", line)
        potassium_match = re.search(r"Potassium:\s*([\d.]+)", line)
        
        # Check if each match was found and extract numeric value
        try:
            data = [
                float(nitrogen_match.group(1)),
                float(phosphorous_match.group(1)),
                float(potassium_match.group(1)),
                float(temperature_match.group(1)),
                float(ec_match.group(1)),  # Assuming EC is being read as humidity
                float(moisture_match.group(1)),
                float(ph_match.group(1))
            ]
            return data  # Returns list of floats as required for the model
        except AttributeError:
            print("Error: One or more sensor values missing or incorrectly formatted.")
            return None

# Load and prepare dataset
data = pd.read_csv('C:/Users/kevin/Desktop/Bhoomi/MainBhoomi/Code/ANN/crop_recommendation.csv')
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label']

# Encode labels and one-hot encode the target
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

# Normalize the input features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define the Neural Network model
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

# Function to predict crop based on sensor data
def predict_crop(sensor_data):
    """Uses the deep learning model to predict the crop based on sensor data."""
    input_data = scaler.transform([sensor_data])
    prediction = model.predict(input_data)
    predicted_class = np.argmax(prediction, axis=1)
    return label_encoder.inverse_transform(predicted_class)[0]

# Main loop to read sensor data and predict crop
while True:
    sensor_data = get_sensor_data()
    if sensor_data:
        # Ensure we received exactly 7 values
        if len(sensor_data) == 7:
            predicted_crop = predict_crop(sensor_data)
            print("Predicted Crop:", predicted_crop)
        else:
            print("Error: Incorrect number of sensor values received.")
    time.sleep(1)
