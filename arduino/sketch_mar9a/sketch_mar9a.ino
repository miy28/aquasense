#include <WiFi.h>
#include <HttpClient.h>
#include <PubSubClient.h>
#include <DS18B20.h>
#include <DallasTemperature.h>
#include <OneWire.h>

// esp32 only supports wpa auth, tower wifi is captive portal (web-based login)
// have to use phone hotspot...

// wifi config
char* ssid = "";
char* pass = "";
char* local_ip = ""; // use laptop/pc ip
char* serverUrl = "http://" + local_ip + ":5000";

// sensor config
const int oneWireBus = 4; // gpio pin for ds18b20
OneWire oneWire(oneWireBus);
DallasTemperature temp_sensor(&oneWire);

void setup() {
  // get serial connection (esp to programmer)
  Serial.begin(115200);

  // get wifi connection
  WiFi.begin(ssid, pass);
  Serial.println("Establishing WiFi connection...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println(".");
  }
  Serial.println("WiFi connection established!");

  // get sensor connection
  temp_sensor.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // int httpResponseCode = http.POST("herro");

    temp_sensor.requestTemperatures();
    float temp_data = temp_sensor.getTempFByIndex(0);

    String jsonPOST = " {\"sensor_type\": \"temp\", 
                        \"value\": " + String(temp_data) + "}";

    int httpResponseCode = http.POST(jsonPOST);

    if(httpResponseCode > 0) {
      Serial.println("Post status: OK (" + httpResponseCode + ")");
    }
    else {
      Serial.println("Post status: No response, failed to send budster (0)");
    }

    http.end();

    delay(10000); // temperature readings every 10 seconds
  }
}
