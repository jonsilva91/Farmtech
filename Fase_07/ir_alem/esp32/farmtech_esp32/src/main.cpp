#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>

// ===== Se seu módulo é BME280 (tem umidade), deixe este include;
// ===== se for BMP280 (sem umidade), veja nota no final.
#include <Adafruit_BME280.h>
Adafruit_BME280 bme;

// ====== CONFIG WIFI/HTTP ======
const char* WIFI_SSID = "SEUSSID";
const char* WIFI_PASS = "SEUPASS";


const char* SERVER_BASE = "http://SEU_IP_LOCAL:5000";
const char* ENDPOINT = "/ingest";

const int SOIL_PIN = 34;   // pino analógico do sensor de solo
const unsigned long SEND_MS = 10000; // envia a cada 10 s
unsigned long lastSend = 0;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }
  Serial.println("\nWiFi OK. IP: " + WiFi.localIP().toString());
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  connectWiFi();
  int id = bme.sensorID(); // em alguns forks funciona
  Serial.printf("sensorID=0x%X\n", id);
  Wire.begin(21, 22); // SDA=21, SCL=22 padrão ESP32
  bool ok = bme.begin(0x76) || bme.begin(0x77);
if (!ok) Serial.println("BME/BMP280 não inicializado (confira solda/SDO/endereco)");



 
  if (!ok) Serial.println("Aviso: BME280 não inicializado (verifique endereço/ligação).");

  analogReadResolution(12); // 0..4095
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  
  unsigned long now = millis();
  if (now - lastSend < SEND_MS) return;
  lastSend = now;

  // Leituras
  float tempC = NAN, umidAr = NAN, press = NAN;
  tempC = bme.readTemperature();
  umidAr = bme.readHumidity();           // se for BMP280, remova esta linha
  press  = bme.readPressure() / 100.0;   // hPa

  int soilRaw = analogRead(SOIL_PIN);
  float soilPct = 100.0f * (4095 - soilRaw) / 4095.0f; // ajuste após calibração

  // Monta JSON
  char body[320];
  snprintf(body, sizeof(body),
    "{"
      "\"cultura\":\"soja\","
      "\"sensor\":\"bme280\","
      "\"temperatura_c\":%.2f,"
      "\"umidade_relativa_pct\":%.2f,"
      "\"pressao_hpa\":%.2f,"
      "\"umidade_solo_raw\":%d,"
      "\"umidade_solo_pct\":%.2f,"
      "\"local\":\"talhao_A\""
    "}",
    tempC, umidAr, press, soilRaw, soilPct
  );

  String url = String(SERVER_BASE) + String(ENDPOINT);
  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST((uint8_t*)body, strlen(body));
  String resp = http.getString();
  http.end();

  Serial.print("POST "); Serial.print(url);
  Serial.print(" -> "); Serial.print(code);
  Serial.print(" | payload: "); Serial.println(body);
  Serial.print("resp: "); Serial.println(resp);
}
