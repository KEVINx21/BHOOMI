#include <WiFi.h>
#include <FirebaseESP32.h>
#include <HardwareSerial.h>

// Wi-Fi credentials
#define WIFI_SSID "iPhone 6"
#define WIFI_PASSWORD "kevin2321"

// GPIO pins for DE (Data Enable) and RE (Receiver Enable)
#define DE 26
#define RE 25

// Sensor command arrays
const byte temp[] = {0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xcf};
const byte mois[] = {0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F};
const byte econ[] = {0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce};
const byte ph[] = {0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b};
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[] = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc};
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0};

byte values[11];
HardwareSerial mod(2); // UART2 (GPIO16 - Rx, GPIO17 - Tx)

float envhumidity = 0.0, envtemperature = 0.0, soil_ph = 0.0, soil_mois = 0.0, soil_temp = 0.0;
byte val1 = 0, val2 = 0, val3 = 0, val4 = 0, val5 = 0, val6 = 0, val7 = 0;

FirebaseData firebaseData;
FirebaseAuth firebaseAuth;
FirebaseConfig firebaseConfig;

const char* FIREBASE_HOST = "bhoomi-21-default-rtdb.asia-southeast1.firebasedatabase.app/";
const char* FIREBASE_AUTH = "xB7VDdVJynT2R6GFtpdpIWeoQE0VHkhdnaiDEGoL";

void setup() {
  Serial.begin(115200);
  mod.begin(9600, SERIAL_8N1, 16, 17);

  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);

  // Set RS-485 to receive mode
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi (config for iPhone6 only)...)");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi, yeaaa!");

  // Set Firebase configuration
  firebaseConfig.host = FIREBASE_HOST;
  firebaseConfig.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&firebaseConfig, &firebaseAuth);
  Firebase.reconnectWiFi(true);

  delay(3000);
}

void loop() {
  // Read sensor values
  val1 = moisture();
  soil_mois = val1 / 1.8;
  delay(1000);

  soil_temp = temperature() / 10.0;
  delay(1000);

  val3 = econduc();
  delay(1000);

  val4 = phydrogen() / 25;
  soil_ph = val4;
  delay(1000);

  val5 = nitrogen();
  delay(1000);

  val6 = phosphorous();
  delay(1000);

  val7 = potassium();
  delay(1000);

  // Display values in Serial Monitor
  Serial.print("Moisture:"); Serial.println(soil_mois);
  Serial.print("Temperature:"); Serial.println(soil_temp);
  Serial.print("EC:"); Serial.println(val3);
  Serial.print("pH:"); Serial.println(soil_ph);
  Serial.print("Nitrogen:" ); Serial.println(val5);
  Serial.print("Phosphorous:"); Serial.println(val6);
  Serial.print("Potassium:"); Serial.println(val7);

  // Upload data to Firebase
  Firebase.setFloat(firebaseData, "/SoilData/Moisture", soil_mois);
  Firebase.setFloat(firebaseData, "/SoilData/Temperature", soil_temp);
  Firebase.setInt(firebaseData, "/SoilData/EC", val3);
  Firebase.setFloat(firebaseData, "/SoilData/pH", soil_ph);
  Firebase.setInt(firebaseData, "/SoilData/Nitrogen", val5);
  Firebase.setInt(firebaseData, "/SoilData/Phosphorous", val6);
  Firebase.setInt(firebaseData, "/SoilData/Potassium", val7);

  if (firebaseData.httpCode() != 200) {
    Serial.print("Firebase Error: ");
    Serial.println(firebaseData.errorReason());
  }

  delay(3000);
}

// Sensor functions
byte moisture() {
  return requestData(mois);
}
byte temperature() {
  return requestData(temp);
}
byte econduc() {
  return requestData(econ);
}
byte phydrogen() {
  return requestData(ph);
}
byte nitrogen() {
  return requestData(nitro);
}
byte phosphorous() {
  return requestData(phos);
}
byte potassium() {
  return requestData(pota);
}

byte requestData(const byte* cmd) {
  mod.flush();

  // Switch RS-485 to transmit mode
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(1);

  // Send command to the sensor
  for (uint8_t i = 0; i < 8; i++) {
    mod.write(cmd[i]);
  }
  mod.flush();

  // Switch back to receive mode
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);
  delay(200);

  // Read response from sensor
  for (byte i = 0; i < 7; i++) {
    values[i] = mod.read();
  }
  return values[4];  // Return relevant data byte
}
