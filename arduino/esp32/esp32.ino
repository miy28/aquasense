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
String ssid = "Anurag";
String pass = "Anurag123";
// String local_ip = "10.195.100.112"; // use laptop/pc ip
String local_ip = "172.20.10.6";
String tempServerUrl = "http://" + local_ip + ":5001/data/temp";
String lightServerUrl = "http://" + local_ip + ":5001/data/light";
String phServerUrl = "http://" + local_ip + ":5001/data/pH";
// String serverUrl = "http://10.195.100.112:5000/data";
// IPAddress localIp(10,195,100,112);
IPAddress localIp(172,20,10,6);

// String local_ip = "";
// String serverUrl = "http://" + local_ip + ":5000/data";
// IPAddress localIp();

// temp sensor config
const int oneWireBus = 0; // gpio pin for ds18b20
OneWire oneWire(oneWireBus);
DallasTemperature temp_sensor(&oneWire);

// light sensor config
const int light_sensor_light = 32;
int lightInit_bright;
int lightVal_bright;
const int light_sensor_dark = 33;
int lightInit_dark;
int lightVal_dark;

// ph sensor config
const int ph_sensor_pin = 2;
const float pH_offset = 0.0;      // Calibration offset
const float pH_linear = 3.5;      // Linear coefficient (depends on sensor)

void setup() {
  pinMode(light_sensor_dark, INPUT);
  pinMode(light_sensor_light, INPUT);
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
  if (!client.connect(localIp, 5001)) {
      Serial.println("Failed to connect to server!");
  } else {
      Serial.println("Connected to Flask server!");
      client.stop();
  }

  // get temp connection
  Serial.println("Establishing DS18B20 Connection...");
  temp_sensor.begin();
  Serial.print("DS18B20 connected: ");
  Serial.print(temp_sensor.getDeviceCount());

  // get light connection
  lightInit_dark = analogRead(light_sensor_dark) * (3.3 / 4095.0);
  lightInit_bright = analogRead(light_sensor_light) * (3.3 / 4095.0);

  // get ph connection

}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // --- Temperature POST ---
    HTTPClient http;
    http.begin(tempServerUrl);  // Temp still goes to /data/temp
    http.addHeader("Content-Type", "application/json");
    
    temp_sensor.requestTemperatures();
    float data_temp = temp_sensor.getTempFByIndex(0);

    String jsonPOST_temp = "{\"sensor_type\": \"temp\", \"value\": " + String(data_temp) + "}";
    int httpResponseCode_temp = http.POST(jsonPOST_temp);

    http.end(); // Close temp HTTP session

    // --- Light Sensors POST ---

    float data_light_dark = analogRead(light_sensor_dark);
    float data_light_bright = analogRead(light_sensor_light);

    HTTPClient http_light_dark;
    http_light_dark.begin(lightServerUrl);
    http_light_dark.addHeader("Content-Type", "application/json");

    String jsonPOST_light_dark = "{\"sensor_type\": \"light_dark\", \"value\": " + String(data_light_dark) + "}";
    int httpResponseCode_light_dark = http_light_dark.POST(jsonPOST_light_dark);

    http_light_dark.end(); // close after POST

    HTTPClient http_light_bright;
    http_light_bright.begin(lightServerUrl);
    http_light_bright.addHeader("Content-Type", "application/json");

    String jsonPOST_light_bright = "{\"sensor_type\": \"light_bright\", \"value\": " + String(data_light_bright) + "}";
    int httpResponseCode_light_bright = http_light_bright.POST(jsonPOST_light_bright);

    http_light_bright.end(); // close after POST

    // --- pH Sensor POST ---

    // Read and average 10 samples for stability
    int raw = 0;
    for(int i = 0; i < 10; i++) {
      raw += analogRead(ph_sensor_pin);
      delay(10);
    }
    raw /= 10;

    // Convert to voltage (0-3.3V range)
    float voltage = raw * (3.3 / 4095.0);

    // Basic pH calculation with temperature compensation
    float data_ph = (7.0 - ((voltage - 2.5) * pH_linear)) + pH_offset;
    data_ph += (25.0 - data_temp) * 0.03; // Temperature compensation

    HTTPClient http_ph;
    http_ph.begin(phServerUrl);
    http_ph.addHeader("Content-Type", "application/json");

    String jsonPOST_ph = "{\"sensor_type\": \"pH\", \"value\": " + String(data_ph) + "}";
    int httpResponseCode_ph = http_ph.POST(jsonPOST_ph);

    http_ph.end(); // close after POST

    // --- Serial Prints ---
    Serial.print("\n");
    Serial.println("temperature: " + String(data_temp));
    Serial.println("dark sensor: " + String(data_light_dark));
    Serial.println("light sensor: " + String(data_light_bright));
    Serial.print("pH sensor: ");
    Serial.println(data_ph, 2);

    if(httpResponseCode_temp > 0 && httpResponseCode_light_dark > 0 && httpResponseCode_light_bright > 0 && httpResponseCode_ph > 0) {
      Serial.print("Post status: OK! (");
      Serial.print(httpResponseCode_temp);
      Serial.print(", ");
      Serial.print(httpResponseCode_light_dark);
      Serial.print(", ");
      Serial.print(httpResponseCode_light_bright);
      Serial.print(", ");
      Serial.print(httpResponseCode_ph);
      Serial.print(")\n");
    }
    else {
      Serial.println("Post status: No response, failed to send. FULCRUM OUT (0)");
    }

    delay(5000); // 5 second delay
  }
}
