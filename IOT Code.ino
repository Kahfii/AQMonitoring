#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

#define DHT_PIN 23     
#define DHT_TYPE DHT11 
#define MQ_PIN 32  

const char* ssid = "FiberHome";
const char* password = "sDDXWsrd";
const char* serverName = "http://IP4_ADDRESS:5000/post-data"; 

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200); 
  dht.begin();
  pinMode(MQ_PIN, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WIFI ..");
  while (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    Serial.print('.');
  }
  Serial.println("Connected to WIFI");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    
    float MQValue = analogRead(MQ_PIN);
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature) || isnan(MQValue)) {
      Serial.println("Failed to read value from sensor!");
    } else {
      Serial.print("Humidity: ");
      Serial.print(humidity);
      Serial.println("%\t");
      Serial.print("Temperature: ");
      Serial.print(temperature);
      Serial.println(" °C");
      Serial.print("MQ Value: ");
      Serial.print(MQValue);
      Serial.println(" ppm");
      
      http.addHeader("Content-Type", "application/json");
      StaticJsonDocument<200> doc;
      doc["Humidity"] = humidity;
      doc["Temperature"] = temperature;
      doc["MQ Value"] = MQValue;

      String requestBody;
      serializeJson(doc, requestBody);

      int httpResponseCode = http.POST(requestBody);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
      } else {
        Serial.println("Failed to post value!");
        Serial.println(httpResponseCode);
      }
      http.end();
    }
  } else {
    Serial.println("WiFi not connected. Attempting to reconnect...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(2000);
      Serial.print('.');
    }
    Serial.println("Reconnected to WIFI");
  }
  delay(5000);
}
