#include <WiFi.h>
#include <PubSubClient.h>
#include <DS18B20.h>
#include <DallasTemperature.h>
#include <OneWire.h>

// esp32 only supports wpa auth, tower wifi is captive portal (web-based login)
// have to use phone hotspot...

char* ssid = "";
char* pass = "";
char* serverUrl = "";

void setup() {
  // put your setup code here, to run once:
  delay(100);
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Establishing WiFi connection...");
  }
  Serial.println("WiFi connection established!");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    // int httpResponseCode = http.POST("herro");

    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);

    String jsonPOST = "{\"sensor\": \"temp\", \"value\": " + String(temp) + "}";

    int httpResponseCode = http.POST(jsonPOST);

    if(httpResponseCode == 200) {
      Serial.println("Post status: OK (" + httpResponseCode + ")");
    }
    http.end();
  }
}
