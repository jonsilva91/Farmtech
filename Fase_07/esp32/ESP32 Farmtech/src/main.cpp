#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// =======================
// CONFIG WIFI + API
// =======================
const char* WIFI_SSID = "Jonas-2.4G";
const char* WIFI_PASS = "jonas1710";

// Exemplo: "http://192.168.0.10:8000/api/leituras/esp32"
const char* API_URL  = "http://192.168.18.224:8000/api/leituras/esp32";

// Área de plantio associada a este ESP32
const int CD_AREA = 8;


// =======================
// LCD
// =======================
#define I2C_ADDR    0x27
#define LCD_COLUMNS 16
#define LCD_ROWS    2

#define I2C_SDA 21
#define I2C_SCL 22

LiquidCrystal_I2C lcd(I2C_ADDR, LCD_COLUMNS, LCD_ROWS);


// =======================
// DHT22
// =======================
#define DHTPIN  32
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);


// =======================
// LEDS
// =======================
#define LED_AZUL_PIN     23   // alerta umidade baixa
#define LED_VERMELHO_PIN 19   // alerta temperatura alta


// =======================
// TEMPO
// =======================
unsigned long ultimoTempo = 0;
const long intervalo = 2000;  // 2 segundos entre ciclos


typedef struct
{
  float temperatura;
  float umidade;
} DhtResult;

int contador = 0;


// =======================
// NPK (simulado)
// =======================
struct NPK
{
  int nitrogenio; // N
  int fosforo;    // P
  int potassio;   // K
};

int serialPlotOption = 0;


// ====== ESTADO GLOBAL PARA INTEGRAÇÃO COM API ======
DhtResult ultimoDht = {NAN, NAN};
NPK ultimoNpk = {0, 0, 0};
bool irrigacaoAtiva = false;
float phSimulado = 6.5;


// =======================
// WIFI + HTTP
// =======================

void conectaWifi() {
  Serial.print("Conectando ao WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 40) { // ~20s
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi conectado! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Falha ao conectar ao WiFi.");
  }
}

void enviaLeituraHttp(int cd_area,
                      int fosforo,
                      int potassio,
                      float umidade,
                      float ph,
                      bool irrigacao)
{
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] WiFi desconectado, tentando reconectar...");
    conectaWifi();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[HTTP] Ainda sem WiFi, abortando envio.");
      return;
    }
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"cd_area\":" + String(cd_area) + ",";
  payload += "\"fosforo\":" + String(fosforo) + ",";
  payload += "\"potassio\":" + String(potassio) + ",";
  payload += "\"umidade\":" + String(umidade, 1) + ",";
  payload += "\"ph\":" + String(ph, 1) + ",";
  payload += "\"irrigacao\":" + String(irrigacao ? 1.0 : 0.0);
  payload += "}";

  Serial.print("[HTTP] Enviando: ");
  Serial.println(payload);

  int code = http.POST(payload);
  Serial.print("[HTTP] Código de resposta: ");
  Serial.println(code);

  http.end();
}


// =======================
// LÓGICA DE SENSORES / SIMULAÇÃO
// =======================

NPK simularNPK()
{
  NPK valores;

  // Gera valores aleatórios dentro de uma faixa típica
  valores.nitrogenio = random(10, 50);   // Nitrogênio em mg/kg
  valores.fosforo    = random(5, 30);    // Fósforo em mg/kg
  valores.potassio   = random(50, 300);  // Potássio em mg/kg

  if (serialPlotOption == 1 ) {
    Serial.print("NPK em mg/kg - ");
    Serial.print("N: ");
    Serial.print(valores.nitrogenio);
    Serial.print(" | P: ");
    Serial.print(valores.fosforo);
    Serial.print(" | K: ");
    Serial.println(valores.potassio);

    // Linha só com os valores para o Serial Plotter
    Serial.print(valores.nitrogenio);
    Serial.print("\t");
    Serial.print(valores.fosforo);
    Serial.print("\t");
    Serial.println(valores.potassio);
  }

  return valores;
}

void alertaUmidade(float u)
{
  // LED - de alerta de umidade baixa.
  if (u <= 30)
  {
    digitalWrite(LED_AZUL_PIN, HIGH);
  }
  else
  {
    digitalWrite(LED_AZUL_PIN, LOW);
  }
}

void alertaTemperatura(float t)
{
  // LED - de alerta de temperatura alta.
  if (t >= 42)
  {
    digitalWrite(LED_VERMELHO_PIN, HIGH);
  }
  else
  {
    digitalWrite(LED_VERMELHO_PIN, LOW);
  }
}

// DHT22 COM SIMULAÇÃO QUANDO NÃO HÁ SENSOR
DhtResult handleDht22()
{
  DhtResult result;

  result.temperatura = dht.readTemperature();
  result.umidade     = dht.readHumidity();

  if (isnan(result.temperatura) || isnan(result.umidade))
  {
    // Sem sensor físico: gera valores simulados
    static float temp_sim = 30.0;
    static float umid_sim = 50.0;

    temp_sim += (random(-3, 4) * 0.2);   // -0.6 a +0.6
    umid_sim += (random(-5, 6) * 0.3);   // -1.5 a +1.5

    if (temp_sim < 20.0) temp_sim = 20.0;
    if (temp_sim > 40.0) temp_sim = 40.0;
    if (umid_sim < 20.0) umid_sim = 20.0;
    if (umid_sim > 80.0) umid_sim = 80.0;

    result.temperatura = temp_sim;
    result.umidade     = umid_sim;
  }
  else
  {
    // Se tiver sensor de verdade, mantém o comportamento de plot
    if (serialPlotOption == 2 ) {
      Serial.print("Temperatura: ");
      Serial.print(result.temperatura);
      Serial.print("°C  |  Umidade: ");
      Serial.print(result.umidade);
      Serial.println("%");

      // Linha só com os valores para o Serial Plotter
      Serial.print(result.temperatura);
      Serial.print("\t");
      Serial.println(result.umidade);
    }
  }

  alertaUmidade(result.umidade);
  alertaTemperatura(result.temperatura);

  return result;
}


// =======================
// SETUP E LOOP
// =======================

void setup()
{
  pinMode(LED_AZUL_PIN, OUTPUT);
  pinMode(LED_VERMELHO_PIN, OUTPUT);

  Serial.begin(115200);
  delay(1000);

  randomSeed(analogRead(0)); // só pra variar simulação

  dht.begin();

  Wire.begin(I2C_SDA, I2C_SCL);
  lcd.begin(LCD_COLUMNS, LCD_ROWS);
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("FarmTech !");
  lcd.setCursor(0, 1);
  lcd.print("Carregando...");

  conectaWifi();

  delay(1000);

  Serial.println("Selecione o Serial Plot:");
  Serial.println("1 - NPK");
  Serial.println("2 - Temperatura e Umidade");
}

void loop()
{
  unsigned long tempoAtual = millis();

  // Leitura opcional do modo de plot via Serial (1 ou 2)
  if (Serial.available() > 0) {
    String entrada = Serial.readString();
    entrada.trim();
    int opt = entrada.toInt();
    serialPlotOption = opt;
  }

  if (tempoAtual - ultimoTempo >= intervalo)
  {
    ultimoTempo = tempoAtual;
    contador++;

    if ((contador % 2) == 0)
    {
      // Leitura (ou simulação) de temperatura/umidade
      DhtResult result = handleDht22();
      ultimoDht = result;

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Temp: ");
      lcd.print(String(result.temperatura, 1));
      lcd.write(223);
      lcd.print("C");

      lcd.setCursor(0, 1);
      lcd.print("Umidade: ");
      lcd.print(String(result.umidade, 1));
      lcd.print("%");
    }
    else
    {
      // Simulação de NPK
      NPK npkResult = simularNPK();
      ultimoNpk = npkResult;

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("NPK - N: ");
      lcd.print(npkResult.nitrogenio);

      lcd.setCursor(0, 1);
      lcd.print("P: ");
      lcd.print(npkResult.fosforo);
      lcd.print(" K: ");
      lcd.print(npkResult.potassio);
    }

    // Deriva irrigacaoAtiva a partir da umidade
    if (!isnan(ultimoDht.umidade)) {
      irrigacaoAtiva = (ultimoDht.umidade <= 30.0);
    }

    phSimulado = 6.5; // fixo só pra compor dado

    // Debug na Serial (opcional)
    Serial.printf(
      "Fosforo: %d | Potassio: %d | Umidade: %.1f%% | pH: %.1f | Irrigacao: %s\n",
      ultimoNpk.fosforo,
      ultimoNpk.potassio,
      ultimoDht.umidade,
      phSimulado,
      irrigacaoAtiva ? "ATIVA" : "INATIVA"
    );

    // Envio para o backend via API (FastAPI)
    enviaLeituraHttp(
      CD_AREA,
      ultimoNpk.fosforo,
      ultimoNpk.potassio,
      ultimoDht.umidade,
      phSimulado,
      irrigacaoAtiva
    );
  }
}
