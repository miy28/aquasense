#include <WiFi.h>
#include <HTTPClient.h>
// #include <PubSubClient.h>
#include <DFRobot_PH.h>
#include <DS18B20.h>
#include <DallasTemperature.h>
#include <OneWire.h>

// esp32 only supports wpa auth, tower wifi is captive portal (web-based login)
// have to use phone hotspot...

// wifi config
String ssid = ""; 
String pass = "";

String local_ip = "";
String serverUrl = "http://" + local_ip + ":5000/data";
IPAddress localIp();

// sensor config
const int oneWireBus = 4; // gpio pin for ds18b20
OneWire oneWire(oneWireBus);
DallasTemperature temp_sensor(&oneWire);

void setup() {
  // get serial connection (esp to programmer)
  Serial.begin(9600);

  // get wifi connection
  Serial.println("Establishing WiFi connection...");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println(".");
  }
  Serial.println("WiFi connection established!");

  Serial.println("Pinging server...");
  WiFiClient client;
  if (!client.connect(localIp, 5000)) {
      Serial.println("Failed to connect to server!");
  } else {
      Serial.println("Connected to Flask server!");
      client.stop();
  }

  // get sensor connection
  Serial.println("Establishing DS18B20 Connection...");
  temp_sensor.begin();
  Serial.println("DS18B20 connected!");
  Serial.println(temp_sensor.getDeviceCount());
}

void loop() {
  // // put your main code here, to run repeatedly:
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // int httpResponseCode = http.POST("herro");

    temp_sensor.requestTemperatures();
    float temp_data = temp_sensor.getTempFByIndex(0);

    String jsonPOST = "{\"sensor_type\": \"temp\", \"value\": " + String(temp_data) + "}";

    int httpResponseCode = http.POST(jsonPOST);

    Serial.println(temp_data);
    Serial.println(httpResponseCode);

    if(httpResponseCode > 0) {
      Serial.println("Post status: OK (");
      Serial.println(httpResponseCode); 
      Serial.println(")");
    }
    else {
      Serial.println("Post status: No response, failed to send budster (0)");
    }

    http.end();

    delay(10000); // temperature readings every 10 seconds
  }
}
