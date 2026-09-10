/*
  =============================================================================
  AgroSentry ESP32 Firmware — Soil Moisture & Light Sensor Node
  =============================================================================
  Target IP: 192.168.31.57
  Connects:
  - Soil Moisture Sensor: Analog Pin (GPIO 34 or GPIO 36)
  - Light Sensor: Analog LDR (GPIO 35) or Digital I2C BH1750 (SDA: 21, SCL: 22)
  
  Features:
  1. Serves sensor data at GET http://192.168.31.57/data
  2. Periodically POSTs sensor data to AgroSentry Server:
     POST http://<YOUR_COMPUTER_IP>:8000/api/telemetry
  =============================================================================
*/

#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>

// ----------------- Wi-Fi Settings -----------------
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Static IP Configuration (for 192.168.31.57)
IPAddress local_IP(192, 168, 31, 57);
IPAddress gateway(192, 168, 31, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);

// AgroSentry Server URL on your laptop/PC (Port 8000)
// Replace with your PC's Wi-Fi IP address:
const char* serverUrl = "http://192.168.31.100:8000/api/telemetry";

// ----------------- Pin Definitions -----------------
#define SOIL_PIN 34   // Analog pin for Soil Moisture (Capacitive or Resistive)
#define LIGHT_PIN 35  // Analog pin for LDR Light Sensor

WebServer server(80);

// Global readings
float soilMoisturePercent = 0.0;
float lightLux = 0.0;
float temperatureC = 25.0; // or attach DHT11/DHT22 to GPIO 4
float humidityPercent = 60.0;

unsigned long lastPostTime = 0;
const unsigned long postInterval = 3000; // Send reading every 3 seconds

// ----------------- Helper Functions -----------------
void readSensors() {
  // Read Soil Moisture (0 - 4095 on ESP32 ADC)
  // Calibrate: dry in air (~3200), wet in water (~1400)
  int rawSoil = analogRead(SOIL_PIN);
  soilMoisturePercent = map(rawSoil, 3200, 1400, 0, 100);
  soilMoisturePercent = constrain(soilMoisturePercent, 0.0, 100.0);

  // Read Light Sensor (LDR on pin 35)
  // 0 is dark, 4095 is direct bright light
  int rawLight = analogRead(LIGHT_PIN);
  lightLux = map(rawLight, 0, 4095, 100, 75000); // Approximate Lux mapping
}

// Handler for GET /data (Pull Mode)
void handleData() {
  readSensors();
  String json = "{";
  json += "\"soil_moisture\":" + String(soilMoisturePercent, 1) + ",";
  json += "\"light_lux\":" + String(lightLux, 0) + ",";
  json += "\"temperature\":" + String(temperatureC, 1) + ",";
  json += "\"humidity\":" + String(humidityPercent, 1);
  json += "}";

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// Push data directly to computer via HTTP POST
void sendDataToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"soil_moisture\":" + String(soilMoisturePercent, 1) + ",";
    json += "\"light_lux\":" + String(lightLux, 0) + ",";
    json += "\"temperature\":" + String(temperatureC, 1) + ",";
    json += "\"humidity\":" + String(humidityPercent, 1);
    json += "}";

    int httpCode = http.POST(json);
    if (httpCode > 0) {
      Serial.printf("[HTTP] POST ok, code: %d\n", httpCode);
    } else {
      Serial.printf("[HTTP] POST failed: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 12-bit ADC

  // Configure Static IP: 192.168.31.57
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS)) {
    Serial.println("STA Failed to configure Static IP");
  }

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Web Server Routes
  server.on("/data", HTTP_GET, handleData);
  server.begin();
  Serial.println("HTTP Server started at http://192.168.31.57/data");
}

void loop() {
  server.handleClient();

  if (millis() - lastPostTime > postInterval) {
    lastPostTime = millis();
    readSensors();
    sendDataToServer();
  }
}
