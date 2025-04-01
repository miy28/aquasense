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
String ssid = "Myke";
String pass = "69696969";
// String local_ip = "10.195.100.112"; // use laptop/pc ip
String local_ip = "172.20.10.5";
String serverUrl = "http://" + local_ip +   ":5000/data";
// String serverUrl = "http://10.195.100.112:5000/data";
// IPAddress localIp(10,195,100,112);
IPAddress localIp(172,20,10,5);

// String local_ip = "";
// String serverUrl = "http://" + local_ip + ":5000/data";
// IPAddress localIp();

// sensor config
const int oneWireBus = 4; // gpio pin for ds18b20
OneWire oneWire(oneWireBus);
DallasTemperature temp_sensor(&oneWire);

void setup() {
  delay(1000);

  // get serial connection (esp to programmer)
  Serial.begin(9600);

  // get wifi connection
  Serial.println("Establishing WiFi connection...");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connection established!");

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
  Serial.print("DS18B20 connected: ");
  Serial.print(temp_sensor.getDeviceCount());
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

    if(temp_data < 0) {
        httpResponseCode = 0;
    }

    Serial.print("\n");
    Serial.println(temp_data);

    if(httpResponseCode > 0) {
      Serial.print("Post status: OK! (");
      Serial.print(httpResponseCode);
      Serial.print(")\n");
    }
    else {
      Serial.println("Post status: No response, failed to send budster (0)");
    }

    http.end();

    delay(10000); // temperature readings every 10 seconds
  }
}
