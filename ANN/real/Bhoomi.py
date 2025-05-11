import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# Load dataset
data = pd.read_csv('crop_recommendation.csv')

# Features and labels
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label']

# Encode crop labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

# Normalize all input features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define Neural Network
model = Sequential([
    Dense(128, input_shape=(7,), activation='relu'),
    Dropout(0.3),
    Dense(256, activation='relu'),
    Dropout(0.4),
    Dense(128, activation='relu'),
    Dense(y_categorical.shape[1], activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.2, verbose=1)

test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\n✅ Test Accuracy: {test_accuracy * 100:.2f}%")

# ==================== Prediction Section ====================
def get_user_input():
    print("\n📥 Enter the following soil and weather values:")
    N = float(input("Nitrogen (N): "))
    P = float(input("Phosphorus (P): "))
    K = float(input("Potassium (K): "))
    temperature = float(input("Temperature (°C): "))
    humidity = float(input("Humidity (%): "))
    ph = float(input("pH value: "))
    rainfall = float(input("Rainfall (mm): "))
    
    input_array = np.array([N, P, K, temperature, humidity, ph, rainfall]).reshape(1, -1)
    return scaler.transform(input_array)  # normalize user input too

# Get input, predict and output result
user_input_scaled = get_user_input()
prediction = model.predict(user_input_scaled)
predicted_class = np.argmax(prediction, axis=1)
predicted_crop = label_encoder.inverse_transform(predicted_class)

# Print result
print("\n🌾 Based on your inputs, the recommended crop is:", predicted_crop[0])
