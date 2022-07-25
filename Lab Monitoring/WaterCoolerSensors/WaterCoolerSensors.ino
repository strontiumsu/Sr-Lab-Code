#include <Wire.h> 
#include <SparkFun_MicroPressure.h> 
#include "SparkFun_AS6212_Qwiic.h" // Library for 12 bit temp sensor
#include <SparkFun_TMP117.h>

#include <WiFi.h> 
#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>

#define DEVICE "ESP32_WATER"
#define TEMP_SENSOR "TMP117"
#define PRESSURE_SENSOR "MPR"
#define FLOW_SENSOR "RFA-2500"

#define WIFI_SSID "EP_PIT_WIFI"                                                                                           //Network Name
#define WIFI_PASSWORD "geodesic"                                                                                          //Network Password
#define INFLUXDB_URL "https://us-east-1-1.aws.cloud2.influxdata.com"                                                      //InfluxDB server url (Use: InfluxDB UI -> Load Data -> Client Libraries)
#define INFLUXDB_TOKEN "ojYiDbgYItxn3IgfzYG7ELnQJmJ3v4KiaGU8ga-RX7dU0NJCaQ_1dzuydWfkOlcMSngKNXJ62wTRmzpiRenUfA=="         //InfluxDB server or cloud API token (Use: InfluxDB UI -> Data -> API Tokens -> <select token>)
#define INFLUXDB_ORG "ejporter@stanford.edu"                                                                              //InfluxDB organization id (Use: InfluxDB UI -> User -> About -> Common Ids )
#define INFLUXDB_BUCKET "Sr Lab Data"                                                                                //InfluxDB bucket name (Use: InfluxDB UI ->  Data -> Buckets)
#define TZ_INFO "PST8PDT"  

SparkFun_MicroPressure mpr1;
SparkFun_MicroPressure mpr2;
TMP117 tempSensor1;
AS6212 tempSensor2;
#define TCAADDR 0x70

float TIN;
float TOUT;
float PIN;
float POUT;
float FLOW;

InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);                 //InfluxDB client instance with preconfigured InfluxCloud certificate

Point sensor("Water Cooling");   

//int analogPin = A3;
//int val = 0;


// choose a mux addr
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

int resetCounter = 0;

void setup() {
  // Start the serial output at 115,200 baud
  Serial.begin(115200);
  Wire.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);     //Setup wifi connection
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wifi connecting...");
    delay(500);
    resetCounter += 1;
    if (resetCounter > 20){
      resetCounter = 0;
      ESP.restart();
    }
  }
  WiFi.mode(WIFI_STA);  
  Serial.println("Wifi connected");//Start serial communication


  if (!tempSensor1.begin(0x4B)){
    Serial.println("temp sensor 1 connection error");
    while(1);
  }
  if (!tempSensor2.begin()){
    Serial.println("temp sensor 2 connection error");
    while(1);
  }
  
  tcaselect(0);
  if (!mpr1.begin()){
    Serial.println("mpr 1 connection error");
    while(1);
  }
  tcaselect(1);
  if (!mpr2.begin()){
    Serial.println("mpr 2 connection error");
    while(1);
  }

  sensor.addTag("device", DEVICE);                               //Add tags
  sensor.addTag("SSID", WIFI_SSID);

  timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");                 //Accurate time is necessary for certificate validation and writing in batches

  if (client.validateConnection())                                   //Check server connection
  {
    Serial.print("Connected to InfluxDB: ");
    Serial.println(client.getServerUrl());
  } 
  else 
  {
    Serial.print("InfluxDB connection failed: ");
    Serial.println(client.getLastErrorMessage());
    Serial.println("Reseting...");
    resetCounter = 0;
    ESP.restart();
  }
}
void loop() {
  if (resetCounter > 20){
    Serial.println("Reseting...");
    resetCounter = 0;
    ESP.restart();
  }
  tcaselect(0);
  PIN = mpr1.readPressure();
  
  tcaselect(1);
  POUT = mpr2.readPressure();
  
  TIN = tempSensor1.readTempC();
  
  TOUT = tempSensor2.readTempC();
  
  // Check if any reads failed and exit early (to try again).
  if (isnan(TIN)) {
    Serial.println(F("Failed to read from temp sensor (IN)!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(TOUT)) {
    Serial.println(F("Failed to read from temp sensor (OUT)!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(PIN)) {
    Serial.println(F("Failed to read from mpr sensor (IN)!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(POUT)) {
    Serial.println(F("Failed to read from mpr sensor (OUT)!"));
    delay(100);
    resetCounter += 1;
    return;
  }

  
  Serial.println("TIN");
  Serial.println(TIN);
  Serial.println("TOUT");
  Serial.println(TOUT);
  Serial.println("PIN");
  Serial.println(PIN);
  Serial.println("POUT");
  Serial.println(POUT);

  sensor.clearFields();
  sensor.addField("TEMP IN", TIN );
  sensor.addField("TEMP OUT", TOUT );
  sensor.addField("PRESSURE IN", PIN );
  sensor.addField("PRESSURE OUT", POUT);

  if (WiFi.status() != WL_CONNECTED)    {                           //Check WiFi connection and reconnect if needed
    Serial.println("Wifi connection lost");
    resetCounter += 1;
    return;
  }
  if (!client.writePoint(sensor))                                    //Write data point
  {
    Serial.print("InfluxDB write failed: ");
    Serial.println(client.getLastErrorMessage());
    resetCounter += 1;
    return;
  }
  
  delay(10*1000);
  resetCounter = 0;
}
