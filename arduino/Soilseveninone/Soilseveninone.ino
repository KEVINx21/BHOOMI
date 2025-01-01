#include <HardwareSerial.h>

// GPIO pins for DE (Data Enable) and RE (Receiver Enable)
#define DE 5  // Can be any GPIO pin
#define RE 4  // Can be any GPIO pin

const byte temp[] = {0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xcf}; 
const byte mois[] = {0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F};
const byte econ[] = {0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce};
const byte ph[] = {0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b};
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[] = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc};
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0};

byte values[11];
HardwareSerial mod(2); // Use UART2 (GPIO16 - Rx, GPIO17 - Tx)

float envhumidity = 0.0, envtemperature = 0.0, soil_ph = 0.0, soil_mois = 0.0, soil_temp = 0.0;
byte val1 = 0, val2 = 0, val3 = 0, val4 = 0, val5 = 0, val6 = 0, val7 = 0;

void setup() {
  Serial.begin(115200);       // Serial monitor
  mod.begin(9600, SERIAL_8N1, 16, 17);  // UART2 (Rx=16, Tx=17)

  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);

  // Set RS-485 to receive mode
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);

  delay(3000);
}

void loop() {
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

  Serial.print("Moisture: "); Serial.print(soil_mois); Serial.println(" %");
  delay(1000);
  
  Serial.print("Temperature: "); Serial.print(soil_temp); Serial.println(" C");
  delay(1000);
  
  Serial.print("EC: "); Serial.print(val3); Serial.println(" us/cm");
  delay(1000);
  
  Serial.print("pH: "); Serial.print(soil_ph); Serial.println(" pH");
  delay(1000);
  
  Serial.print("Nitrogen: "); Serial.print(val5); Serial.println(" mg/kg");
  delay(1000);
  
  Serial.print("Phosphorous: "); Serial.print(val6); Serial.println(" mg/kg");
  delay(1000);
  
  Serial.print("Potassium: "); Serial.print(val7); Serial.println(" mg/kg");
  Serial.println();
  delay(3000);
}

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
