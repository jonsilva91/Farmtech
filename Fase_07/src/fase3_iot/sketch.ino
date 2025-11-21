#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// LCD
#define I2C_ADDR 0x27
#define LCD_COLUMNS 16
#define LCD_ROWS 2

#define I2C_SDA 21
#define I2C_SCL 22

LiquidCrystal_I2C lcd(I2C_ADDR, LCD_COLUMNS, LCD_ROWS);

// DHT22
#define DHTPIN 32
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

// LEDS
#define LED_AZUL_PIN 23
#define LED_VERMELHO_PIN 19

unsigned long ultimoTempo = 0;
const long intervalo = 1000;

typedef struct
{
  float temperatura;
  float umidade;
} DhtResult;

int contador;

struct NPK
{
  int nitrogenio; // N
  int fosforo;    // P
  int potassio;   // K
};

int serialPlotOption = 0;

// ====== NOVOS ESTADOS GLOBAIS PARA UNIFICAR LEITURAS ======
DhtResult ultimoDht = {NAN, NAN};
NPK ultimoNpk = {0, 0, 0};
bool irrigacaoAtiva = false;   // vamos derivar isso da umidade
float phSimulado = 6.5;        // pH fictício só para compor a linha oficial
// =========================================================


// Função que gera valores simulados para NPK
NPK simularNPK()
{
  NPK valores;

  // Gera valores aleatórios dentro de uma faixa típica
  valores.nitrogenio = random(10, 50); // Nitrogênio em mg/kg
  valores.fosforo = random(5, 30);     // Fósforo em mg/kg
  valores.potassio = random(50, 300);  // Potássio em mg/kg

  if (serialPlotOption == 1 ) {
    Serial.print("NPK em mg/kg - ");
    Serial.print("N: ");
    Serial.print(valores.nitrogenio);
    Serial.print("| P: ");
    Serial.print(valores.fosforo);
    Serial.print("| K: ");
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

void setup()
{
  pinMode(LED_AZUL_PIN, OUTPUT);
  pinMode(LED_VERMELHO_PIN, OUTPUT);

  // DHT - setup
  Serial.begin(115200);
  dht.begin();

  // LCD - setup
  Wire.begin(I2C_SDA, I2C_SCL);

  lcd.begin(LCD_COLUMNS, LCD_ROWS);
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("FarmTech !");

  lcd.setCursor(0, 1);
  lcd.print("Carregando...");

  delay(1000);

  Serial.println("Selecione o Serial Plot:");
  Serial.println("1 - NPK:");
  Serial.println("2 - Temperatura e Umidade:");
}

DhtResult handleDht22()
{
  DhtResult result;

  result.temperatura = dht.readTemperature();
  result.umidade = dht.readHumidity();

  if (isnan(result.temperatura) || isnan(result.umidade))
  {
    Serial.println("Falha ao ler o sensor DHT22!");
    return result;
  }

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

  // Ativa/desativa LEDs de alerta com base nos valores reais
  alertaUmidade(result.umidade);
  alertaTemperatura(result.temperatura);

  return result;
}

void loop()
{
  unsigned long tempoAtual = millis();

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

    // Alterna entre DHT e NPK na LCD, como você já fazia
    if ((contador % 2) == 0)
    {
      DhtResult result = handleDht22();
      ultimoDht = result; // ====== GUARDA ÚLTIMA LEITURA DE DHT ======

      lcd.clear();

      lcd.setCursor(0, 0);
      lcd.print("Temp: ");
      lcd.print(String(result.temperatura, 2));
      lcd.write(223);
      lcd.print("C");

      lcd.setCursor(0, 1);
      lcd.print("Umidade: " + String(result.umidade, 1) + "%");
    }
    else
    {
      NPK npkResult = simularNPK();
      ultimoNpk = npkResult; // ====== GUARDA ÚLTIMA LEITURA DE NPK ======

      lcd.clear();

      lcd.setCursor(0, 0);
      lcd.print("NPK - ");
      lcd.print("N: ");
      lcd.print(npkResult.nitrogenio);

      lcd.setCursor(0, 1);
      lcd.print("P: ");
      lcd.print(npkResult.fosforo);
      lcd.print("| K: ");
      lcd.print(npkResult.potassio);
    }

    // ====== AQUI ENTRA A LINHA "OFICIAL" PARA A FASE 7 ======

    // Deriva irrigacaoAtiva a partir da umidade do ar (simples)
    if (!isnan(ultimoDht.umidade)) {
      irrigacaoAtiva = (ultimoDht.umidade <= 30.0);
    }

    // pH simulado (fixo, só para compor o protocolo de dados)
    phSimulado = 6.5;

    // Linha única que o Python (esp32_serial.py) vai consumir
    Serial.printf(
      "Fosforo: %d | Potassio: %d | Umidade: %.1f%% | pH: %.1f | Irrigacao: %s\n",
      ultimoNpk.fosforo,
      ultimoNpk.potassio,
      ultimoDht.umidade,
      phSimulado,
      irrigacaoAtiva ? "ATIVA" : "INATIVA"
    );
  }
}
