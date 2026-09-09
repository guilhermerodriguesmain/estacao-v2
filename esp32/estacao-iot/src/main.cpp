#include <Arduino.h>
#include <Wire.h>
#include <RTClib.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

//wifi config
#define AP_SSID "ESP32_CONFIG"
#define AP_PASSWORD "12345678"
#define WIFI_TIMEOUT 15000
WebServer server(80);
Preferences preferences;

String redesDisponiveis[20];
int quantidadeRedes = 0;

// pinout RTC_ds3231
#define SDA_PIN  21 //jumper laranja
#define SCL_PIN  22 //jumper azul
RTC_DS3231 rtc;

// pinout DHT11
#define DHTPIN 4 // jumper verde
#define DHTTYPE    DHT11    
DHT_Unified dht(DHTPIN, DHTTYPE);

// controle de horario de envio de dados para api
uint32_t ultimaHoraEnviada = 0;

// CONECTAR AO WIFI

bool conectarWiFi(String ssid, String senha)
{
    Serial.println();
    Serial.println("================================");
    Serial.println("Tentando conectar ao Wi-Fi...");
    Serial.println("SSID: " + ssid);
    Serial.println("================================");

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), senha.c_str());

    unsigned long inicio = millis();

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");

        if (millis() - inicio >= WIFI_TIMEOUT)
        {
            Serial.println();
            Serial.println("Falha na conexão.");

            WiFi.disconnect(true);
            delay(500);

            return false;
        }
    }

    Serial.println();
    Serial.println("================================");
    Serial.println("Wi-Fi conectado com sucesso!");
    Serial.println("================================");

    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());

    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    Serial.print("Gateway: ");
    Serial.println(WiFi.gatewayIP());

    Serial.print("Máscara: ");
    Serial.println(WiFi.subnetMask());

    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    Serial.print("MAC: ");
    Serial.println(WiFi.macAddress());

    Serial.println();

    return true;
}



// SCAN DAS REDES


void escanearRedes()
{
    Serial.println();
    Serial.println("================================");
    Serial.println("Escaneando redes Wi-Fi...");
    Serial.println("================================");

    WiFi.mode(WIFI_STA);

    int total = WiFi.scanNetworks();

    quantidadeRedes = 0;

    if (total <= 0)
    {
        Serial.println("Nenhuma rede encontrada.");
        return;
    }

    Serial.print(total);
    Serial.println(" redes encontradas:");

    for (int i = 0; i < total && quantidadeRedes < 20; i++)
    {
        redesDisponiveis[quantidadeRedes] = WiFi.SSID(i);

        Serial.print(i + 1);
        Serial.print(" - ");
        Serial.print(WiFi.SSID(i));
        Serial.print(" | RSSI: ");
        Serial.print(WiFi.RSSI(i));
        Serial.print(" dBm | ");

        if (WiFi.encryptionType(i) == WIFI_AUTH_OPEN)
        {
            Serial.println("Aberta");
        }
        else
        {
            Serial.println("Protegida");
        }

        quantidadeRedes++;
    }

    WiFi.scanDelete();

    Serial.println();
}

// INICIAR ACCESS POINT

void iniciarAP()
{
    Serial.println();
    Serial.println("================================");
    Serial.println("Iniciando modo AP...");
    Serial.println("================================");

    WiFi.disconnect(true);
    delay(500);

    WiFi.mode(WIFI_AP);

    WiFi.softAP(AP_SSID, AP_PASSWORD);

    IPAddress ip = WiFi.softAPIP();

    Serial.print("AP: ");
    Serial.println(AP_SSID);

    Serial.print("Senha: ");
    Serial.println(AP_PASSWORD);

    Serial.print("IP do ESP32: ");
    Serial.println(ip);

    Serial.println();
    Serial.println("Conecte-se à rede");
    Serial.println(AP_SSID);

    Serial.println("Depois acesse:");
    Serial.println("http://192.168.4.1");

    Serial.println();
}



// PÁGINA WEB


String gerarPagina()
{
    String html;

    html += "<!DOCTYPE html>";
    html += "<html>";
    html += "<head>";

    html += "<meta charset='UTF-8'>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";

    html += "<title>Configuração Wi-Fi</title>";

    html += "<style>";

    html += "body{";
    html += "font-family:Arial;";
    html += "background:#f2f2f2;";
    html += "margin:0;";
    html += "padding:20px;";
    html += "}";

    html += ".container{";
    html += "max-width:400px;";
    html += "margin:auto;";
    html += "background:white;";
    html += "padding:25px;";
    html += "border-radius:10px;";
    html += "}";

    html += "input,select{";
    html += "width:100%;";
    html += "padding:10px;";
    html += "margin-top:5px;";
    html += "margin-bottom:15px;";
    html += "box-sizing:border-box;";
    html += "}";

    html += "button{";
    html += "width:100%;";
    html += "padding:12px;";
    html += "background:#333;";
    html += "color:white;";
    html += "border:none;";
    html += "border-radius:5px;";
    html += "}";

    html += "</style>";

    html += "</head>";

    html += "<body>";

    html += "<div class='container'>";

    html += "<h2>Configuração Wi-Fi</h2>";

    html += "<form action='/conectar' method='POST'>";

    html += "<label>Rede Wi-Fi</label>";

    html += "<select name='ssid'>";

    for (int i = 0; i < quantidadeRedes; i++)
    {
        html += "<option value='" + redesDisponiveis[i] + "'>";
        html += redesDisponiveis[i];
        html += "</option>";
    }

    html += "</select>";

    html += "<label>Senha</label>";

    html += "<input type='password' name='senha' placeholder='Senha do Wi-Fi'>";

    html += "<button type='submit'>Conectar</button>";

    html += "</form>";

    html += "</div>";

    html += "</body>";

    html += "</html>";

    return html;
}


// =====================================================
// ROTA PRINCIPAL
// =====================================================

void handleRoot()
{
    server.send(200, "text/html", gerarPagina());
}


// =====================================================
// TENTATIVA DE CONEXÃO PELO FORMULÁRIO
// =====================================================

void handleConectar()
{
    if (!server.hasArg("ssid") || !server.hasArg("senha"))
    {
        server.send(400, "text/plain", "SSID ou senha não informados.");
        return;
    }

    String ssid = server.arg("ssid");
    String senha = server.arg("senha");

    Serial.println();
    Serial.println("================================");
    Serial.println("Nova configuração recebida");
    Serial.println("================================");

    Serial.print("SSID: ");
    Serial.println(ssid);

    // Para de atender requisições enquanto tenta conectar
    server.send(
        200,
        "text/html",
        "<html><body>"
        "<h2>Tentando conectar...</h2>"
        "<p>Verifique o terminal serial.</p>"
        "</body></html>"
    );

    delay(1000);

    // Desliga o servidor
    server.stop();

    // Desliga o AP
    WiFi.softAPdisconnect(true);

    // Tenta conectar
    bool conectado = conectarWiFi(ssid, senha);

    if (conectado)
    {
        // Salva as credenciais
        preferences.begin("wifi", false);

        preferences.putString("ssid", ssid);
        preferences.putString("senha", senha);

        preferences.end();

        Serial.println("Credenciais salvas.");
        Serial.println("ESP32 operando em modo STA.");
    }
    else
    {
        Serial.println();
        Serial.println("Não foi possível conectar.");
        Serial.println("Voltando para modo AP...");

        delay(1000);

        escanearRedes();

        iniciarAP();

        server.on("/", handleRoot);
        server.on("/conectar", HTTP_POST, handleConectar);

        server.begin();

        Serial.println("Servidor web reiniciado.");
    }
}

String criarTimestamp(
    int ano,
    int mes,
    int dia,
    int hora,
    int minuto,
    int segundo
)
{
    char timestamp[25];

    sprintf(
        timestamp,
        "%04d-%02d-%02dT%02d:%02d:%02d",
        ano,
        mes,
        dia,
        hora,
        minuto,
        segundo
    );

    return String(timestamp);
}


String criarJSON(
    float temperatura,
    float umidade,
    int ano,
    int mes,
    int dia,
    int hora,
    int minuto,
    int segundo
)
{
    StaticJsonDocument<200> doc;

    doc["timestamp"] = criarTimestamp(
        ano,
        mes,
        dia,
        hora,
        minuto,
        segundo
    );

    doc["temperatura"] = temperatura;
    doc["umidade"] = umidade;

    String json;

    serializeJson(doc, json);

    return json;
}

void enviarMedicao(String json) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi desconectado");
        return;
    }

    HTTPClient http;
    http.begin("https://minimeteorolia-1.onrender.com/medicoes"); 
    http.addHeader("Content-Type", "application/json");

    int status = http.POST(json);

    Serial.print("Status da API: ");
    Serial.println(status);
    Serial.println(http.getString());

    http.end();
}

void setup() {
  

  Serial.begin(9600);

  //configura pinos I2C do RTC
  Wire.begin(SDA_PIN, SCL_PIN);

  // verifica se o rtc foi encontrado e ou iniciado
  if(!rtc.begin()){
    Serial.println("RTC não encontrado");
    while(1) delay(10);
  }
  Serial.println("RTC inicializado");

  // verifica se o rtc perdeu energia e ajusta a hora
  if (rtc.lostPower())
{
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
}
  delay(10);

  dht.begin();
  Serial.println("DHT 11 inicializado");
  delay(2000);

// conexão wifi

    Serial.println();
    Serial.println("================================");
    Serial.println("        ESP32 Wi-Fi");
    Serial.println("================================");

    // Inicializa armazenamento
    preferences.begin("wifi", true);

    String ssid = preferences.getString("ssid", "");
    String senha = preferences.getString("senha", "");

    preferences.end();

    // -------------------------------------------------
    // Se já existem credenciais salvas
    // -------------------------------------------------

    if (ssid != "")
    {
        Serial.println("Credenciais salvas encontradas.");

        if (conectarWiFi(ssid, senha))
        {
            return;
        }

        Serial.println();
        Serial.println("Credenciais salvas não funcionaram.");
    }
    else
    {
        Serial.println("Nenhuma rede configurada.");
    }

    // -------------------------------------------------
    // Falhou → modo configuração
    // -------------------------------------------------

    escanearRedes();

    iniciarAP();

    server.on("/", handleRoot);
    server.on("/conectar", HTTP_POST, handleConectar);

    server.begin();

    Serial.println("Servidor web iniciado.");
  
}


void loop() {
  

  float temperatura = rtc.getTemperature();
  DateTime data_hora = rtc.now();
  char formato[] = "DD/MM/YYYY hh:mm:ss";

  sensors_event_t umidade;
  dht.humidity().getEvent(&umidade);
  sensors_event_t temperatura_dht;
  dht.temperature().getEvent(&temperatura_dht);

  String json = criarJSON(
    temperatura_dht.temperature,
    umidade.relative_humidity,
    data_hora.year(), //ano
    data_hora.month(), //mes
    data_hora.day(), //dia
    data_hora.hour(), //hora
    data_hora.minute(), //minuto
    data_hora.second()//segundo
);
// envia os dados para a API de hora em hora

uint32_t horaAtual = data_hora.unixtime() / 3600;

if (data_hora.minute() == 0 && horaAtual != ultimaHoraEnviada)
{
    enviarMedicao(json);

    ultimaHoraEnviada = horaAtual;
}
//enviarMedicao(json);

Serial.println(json);

  // impressão de dados no terminal
  
  Serial.println("RTC data");
  Serial.print("temperatura: ");
  Serial.print(temperatura);
  Serial.print(" data: ");
  Serial.print(data_hora.toString(formato));
  Serial.println();
  Serial.println("----------------------------");
  Serial.println();

  Serial.println("DHT data");

  if (isnan(umidade.relative_humidity)) {
    Serial.println("Erro na umidade!");
  } else{
    Serial.print("umidade: ");
    Serial.print(umidade.relative_humidity);
    Serial.print(" %");
  }
  
  Serial.print(" temperatura: ");
  Serial.print(temperatura_dht.temperature);
  Serial.println();
  Serial.println("---------------------------");
  Serial.println();
  
  delay(30000);

   server.handleClient();

}
