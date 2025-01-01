import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential #The Keras model that allows building the neural network.
from tensorflow.keras.layers import Dense, Dropout #Regularization technique to prevent overfitting.
from tensorflow.keras.utils import to_categorical #Converts categorical labels to one-hot encoded vectors.

data = pd.read_csv('crop_recommendation.csv')

X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label'] 

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded) #Converts the numerical labels into one-hot encoding format.For example, if there are 3 crops, the encoding for "Wheat" could be [1, 0, 0], for "Rice" it could be [0, 1, 0], and so on.

X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

# Normalize the input features
scaler = StandardScaler() # so that they have a mean of 0 and a standard deviation of 1. This helps the neural network to train more efficiently.
X_train = scaler.fit_transform(X_train) #calculate the scaling parameters (mean and standard deviation)
X_test = scaler.transform(X_test)

# Define the Fully Connected Neural Network (FCNN) model
model = Sequential([
    Dense(64, input_shape=(7,), activation='relu'),  #LAYER1 :  7 input features and 64 neurons, relu Act func for input layer
    Dropout(0.3), #A dropout layer that randomly drops 30% of the neurons during training to prevent overfitting.
    Dense(128, activation='relu'), # Layer2 : 128 neurons
    Dropout(0.3), # same as above
    Dense(64, activation='relu'), # LAYER3: 64 neurons 
    Dense(y_categorical.shape[1], activation='softmax')  # Output layer with softmax for classification for a probability
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) # adam: optimizer to reduce loss funct

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.2, verbose=1) #verbose prints the training in output

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
test_accuracy = test_accuracy * 100
print(f'Test Accuracy: {test_accuracy:.2f}%')

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
