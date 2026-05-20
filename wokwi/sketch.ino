#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>

// WiFi
const char* ssid     = "Wokwi-GUEST";
const char* password = "";

// URL Flask
const char* serverURL = "https://proyeksbdkelas-boschmonitor.onrender.com/telemetry";

const char* MOTOR_ID = "MOTOR_01";

#define DHT_PIN 4
#define DHT_TYPE DHT22

Adafruit_MPU6050 mpu;
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);

  // connect WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // init MPU6050
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
    while (1);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.println("MPU6050 OK");

  // init DHT22
  dht.begin();
  Serial.println("DHT22 OK");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    WiFi.begin(ssid, password);
    delay(2000);
    return;
  }

  // baca MPU6050
  sensors_event_t a, g, temp_mpu;
  mpu.getEvent(&a, &g, &temp_mpu);

  // baca DHT22
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("DHT22 read failed, skip.");
    delay(1000);
    return;
  }

  // build JSON payload
  StaticJsonDocument<256> doc;
  doc["motor_id"] = MOTOR_ID;
  doc["ax"]       = a.acceleration.x;
  doc["ay"]       = a.acceleration.y;
  doc["az"]       = a.acceleration.z;
  doc["gx"]       = g.gyro.x;
  doc["gy"]       = g.gyro.y;
  doc["gz"]       = g.gyro.z;
  doc["temp"]     = temp;
  doc["hum"]      = hum;

  String payload;
  serializeJson(doc, payload);

  // kirim HTTP POST
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  int responseCode = http.POST(payload);

  if (responseCode > 0) {
    Serial.printf("Response: %d | %s\n", responseCode, http.getString().c_str());
  } else {
    Serial.printf("HTTP Error: %s\n", http.errorToString(responseCode).c_str());
  }

  http.end();
  delay(1000); // kirim tiap 1 detik
}   