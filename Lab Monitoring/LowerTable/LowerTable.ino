#include <Wire.h> 
#include <SparkFun_TMP117.h>            // Used to send and recieve specific information from our sensor
#include <SparkFun_Qwiic_Humidity_AHT20.h>
#include <SparkFun_MicroPressure.h> 

#include <WiFi.h> 
#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>

#define DEVICE "ESP32_LOWER_TABLE"
#define TEMP_SENSOR "TMP117"
#define PRESSURE_SENSOR "MPR"
#define HUMIDITY_SENSOR "AHT20"

#define WIFI_SSID "EP_PIT_WIFI"                                                                                           //Network Name
#define WIFI_PASSWORD "geodesic"                                                                                          //Network Password
#define INFLUXDB_URL "https://us-east-1-1.aws.cloud2.influxdata.com"                                                      //InfluxDB server url (Use: InfluxDB UI -> Load Data -> Client Libraries)
#define INFLUXDB_TOKEN "ojYiDbgYItxn3IgfzYG7ELnQJmJ3v4KiaGU8ga-RX7dU0NJCaQ_1dzuydWfkOlcMSngKNXJ62wTRmzpiRenUfA=="         //InfluxDB server or cloud API token (Use: InfluxDB UI -> Data -> API Tokens -> <select token>)
#define INFLUXDB_ORG "ejporter@stanford.edu"                                                                              //InfluxDB organization id (Use: InfluxDB UI -> User -> About -> Common Ids )
#define INFLUXDB_BUCKET "Sr Lab Data"                                                                                //InfluxDB bucket name (Use: InfluxDB UI ->  Data -> Buckets)
#define TZ_INFO "PST8PDT"  

SparkFun_MicroPressure mpr;
TMP117 tempSensor;
AHT20 humiditySensor;

float T;
float P;
float H;


int resetCounter = 0;

InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);                 //InfluxDB client instance with preconfigured InfluxCloud certificate

Point sensor("Lower Table");   


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


  if (!tempSensor.begin()){
    Serial.println("temp sensor connection error");
    while(1);
  }
 
  if (!mpr.begin()){
    Serial.println("mpr connection error");
    while(1);
  }
  if (!humiditySensor.begin()){
    Serial.println("humidity densor connection error");
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
  
  P = mpr.readPressure();
  T = tempSensor.readTempC();
  H = humiditySensor.getHumidity();

  
  // Check if any reads failed and exit early (to try again).
  if (isnan(T)) {
    Serial.println(F("Failed to read from temp sensor!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(H)) {
    Serial.println(F("Failed to read from humidity sensor!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(P)) {
    Serial.println(F("Failed to read from mpr sensor!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  Serial.println("T");
  Serial.println(T);
  Serial.println("P");
  Serial.println(P);
  Serial.println("H");
  Serial.println(H);

  sensor.clearFields();
  sensor.addField("T", T );
  sensor.addField("P", P );
  sensor.addField("H", H );

  if (WiFi.status() != WL_CONNECTED)  {                                //Check WiFi connection and reconnect if needed
    Serial.println("Wifi connection lost");
    resetCounter += 1;
    Serial.println("connection fail");
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
