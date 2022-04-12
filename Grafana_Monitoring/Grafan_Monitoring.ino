#include <Wire.h>                       
#include <SparkFun_TMP117.h>           
#include <SparkFun_Qwiic_Humidity_AHT20.h>
#include <SparkFun_MicroPressure.h> 

#include <Arduino.h>
#include <PromLokiTransport.h>
#include <PrometheusArduino.h>

#include "certificates.h"   ///DO I STILL NEED THIS
#include "config.h"

//Sensors
TMP117 tempSensor;
AHT20 humiditySensor;
SparkFun_MicroPressure mpr;

// Prometheus client and transport
PromLokiTransport transport;
PromClient client(transport);

// Create a write request for 3 series
WriteRequest req(3, 1537);

// Define a TimeSeries which can hold up to 5 samples, has a name of `temperature/humidity/...` and uses the above labels of which there are 2
TimeSeries ts1(5, "temperature_celsius", "{monitoring_type=\"lab_data\",board_type=\"redboard_esp32\",room=\"lab\"}");
TimeSeries ts2(5, "humidity_percent",  "{monitoring_type=\"lab_data\",board_type=\"redboard_esp32\",room=\"lab\"}");
TimeSeries ts3(5, "pressure_psi",  "{monitoring_type=\"lab_data\",board_type=\"redboard_esp32\",room=\"lab\"}");

int loopCounter = 0;

// Function to set up Prometheus client
void setupClient() {
  Serial.println("Setting up client...");
  
  uint8_t serialTimeout;
  while (!Serial && serialTimeout < 50) {
    delay(100);
    serialTimeout++;
  }
  
  // Configure and start the transport layer
  transport.setUseTls(true);
  transport.setCerts(grafanaCert, strlen(grafanaCert));
  transport.setWifiSsid(WIFI_SSID);
  transport.setWifiPass(WIFI_PASSWORD);
  transport.setDebug(Serial);  // Remove this line to disable debug logging of the client.
  if (!transport.begin()) {
      Serial.println(transport.errmsg);
      while (true) {};
  }

  // Configure the client
  client.setUrl(GC_PROM_URL);
  client.setPath(GC_PROM_PATH);
  client.setPort(GC_PORT);
  client.setUser(GC_PROM_USER);
  client.setPass(GC_PROM_PASS);
  client.setDebug(Serial);  // Remove this line to disable debug logging of the client.
  if (!client.begin()) {
      Serial.println(client.errmsg);
      while (true) {};
  }

  // Add our TimeSeries to the WriteRequest
  req.addTimeSeries(ts1);
  req.addTimeSeries(ts2);
  req.addTimeSeries(ts3);
  req.setDebug(Serial);  // Remove this line to disable debug logging of the write request serialization and compression.
}


// ========== MAIN FUNCTIONS: SETUP & LOOP ========== 
// SETUP: Function called at boot to initialize the system
void setup() {
  // Start the serial output at 115,200 baud
  Serial.begin(115200);

  // Set up client
  setupClient();

  // Start the sensors
  tempSensor.begin();
  humiditySensor.begin()
  mpr.begin()
}


// LOOP: Function called in a loop to read from sensors and send them do databases
void loop() {
  int64_t time;
  time = transport.getTimeMillis();

  // Read temperature and humidity
  float temp = tempSensor.readTempC();
  float hum = humiditySensor.getHumidity();
  float press = mpr.readPressure()
  
  // Check if any reads failed and exit early (to try again).
  if (isnan(temp) || isnan(num) || isnan(press)) {
    Serial.println(F("Failed to read from sensors!"));
    return;
  }

  if (loopCounter >= 5) {
    //Send
    loopCounter = 0;
    PromClient::SendResult res = client.send(req);
    if (!res == PromClient::SendResult::SUCCESS) {
            Serial.println(client.errmsg);
    }
    
    // Reset batches after a succesful send.
    ts1.resetSamples();
    ts2.resetSamples();
    ts3.resetSamples();
  } else {
    if (!ts1.addSample(time, cels)) {
      Serial.println(ts1.errmsg);
    }
    if (!ts2.addSample(time, hum)) {
      Serial.println(ts2.errmsg);
    }
    if (!ts3.addSample(time, hic)) {
      Serial.println(ts3.errmsg);
    }
    loopCounter++;
  }
  // wait INTERVAL seconds and then do it again
  delay(INTERVAL * 1000);
}
