#include <HardwareSerial.h>
#include <Ethernet.h>

// RO to GPIO16 & DI to GPIO17 when using Serial1
#define RE 6  // RS485 Receive Enable (Low to Receive)
#define DE 7  // RS485 Driver Enable (High to Transmit)

const byte temp[] = {0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xcf};  // temperature
const byte mois[] = {0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F};   // moisture
const byte econ[] = {0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce};   // electrical conductivity
const byte ph[] = {0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b};     // pH
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};  // nitrogen
const byte phos[] = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc};   // phosphorus
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0};   // potassium

byte values[11];
HardwareSerial mod(1);  // Use Serial1 (pins GPIO16 and GPIO17)

float envhumidity = 0.0, envtemperature = 0.0, soil_ph = 0.0, soil_mois = 0.0, soil_temp = 0.0;
byte val1 = 0, val2 = 0, val3 = 0, val4 = 0, val5 = 0, val6 = 0, val7 = 0;

void setup() {
  Serial.begin(9600);         // Debugging on Serial
  mod.begin(9600, SERIAL_8N1, 16, 17);  // RS-485 communication on GPIO16 (RX) and GPIO17 (TX)

  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);

  // put RS-485 into receive mode
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

  Serial.print("Moisture: ");
  Serial.print(soil_mois);
  Serial.println(" %");
  delay(1000);
  Serial.print("Temperature: ");
  Serial.print(soil_temp);
  Serial.println(" C");
  delay(1000);
  Serial.print("EC: ");
  Serial.print(val3);
  Serial.println(" us/cm");
  delay(1000);
  Serial.print("pH: ");
  Serial.print(soil_ph);
  Serial.println(" pH");
  delay(1000);
  Serial.print("Nitrogen: ");
  Serial.print(val5);
  Serial.println(" mg/kg");
  delay(1000);
  Serial.print("Phosphorus: ");
  Serial.print(val6);
  Serial.println(" mg/kg");
  delay(1000);
  Serial.print("Potassium: ");
  Serial.print(val7);
  Serial.println(" mg/kg");
  Serial.println();
  delay(3000);
}

byte moisture() {
  mod.flush();
  switchToTransmit();
  sendCommand(mois);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

byte temperature() {
  mod.flush();
  switchToTransmit();
  sendCommand(temp);
  switchToReceive();
  delay(200);
  readResponse();
  return (values[3] << 8 | values[4]);
}

byte econduc() {
  mod.flush();
  switchToTransmit();
  sendCommand(econ);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

byte phydrogen() {
  mod.flush();
  switchToTransmit();
  sendCommand(ph);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

byte nitrogen() {
  mod.flush();
  switchToTransmit();
  sendCommand(nitro);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

byte phosphorous() {
  mod.flush();
  switchToTransmit();
  sendCommand(phos);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

byte potassium() {
  mod.flush();
  switchToTransmit();
  sendCommand(pota);
  switchToReceive();
  delay(200);
  readResponse();
  return values[4];
}

void switchToTransmit() {
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(1);
}

void switchToReceive() {
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);
}

void sendCommand(const byte *command) {
  for (uint8_t i = 0; i < 8; i++) mod.write(command[i]);
  mod.flush();
}

void readResponse() {
  for (byte i = 0; i < 7; i++) {
    values[i] = mod.read();
  }
}
