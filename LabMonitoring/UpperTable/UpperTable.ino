#include <Wire.h> 
#include <SparkFun_TMP117.h>            // Used to send and recieve specific information from our sensor

#include <HTTPClient.h>
#include <Arduino_JSON.h>

#include <WiFi.h> 
#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>

#define DEVICE "ESP32_UPPER_TABLE"
#define TEMP_SENSOR "TMP117"


#define WIFI_SSID "EP_PIT_WIFI"                                                                                           //Network Name
#define WIFI_PASSWORD "geodesic"                                                                                          //Network Password

#define INFLUXDB_URL "https://us-east-1-1.aws.cloud2.influxdata.com"                                                      //InfluxDB server url (Use: InfluxDB UI -> Load Data -> Client Libraries)
#define INFLUXDB_TOKEN "ojYiDbgYItxn3IgfzYG7ELnQJmJ3v4KiaGU8ga-RX7dU0NJCaQ_1dzuydWfkOlcMSngKNXJ62wTRmzpiRenUfA=="         //InfluxDB server or cloud API token (Use: InfluxDB UI -> Data -> API Tokens -> <select token>)
#define INFLUXDB_ORG "ejporter@stanford.edu"                                                                              //InfluxDB organization id (Use: InfluxDB UI -> User -> About -> Common Ids )
#define INFLUXDB_BUCKET "Sr Lab Data"                                                                                //InfluxDB bucket name (Use: InfluxDB UI ->  Data -> Buckets)
#define TZ_INFO "PST8PDT"  

TMP117 tempSensor;

float T;
String openWeatherMapApiKey = "1d2beba230f0d85b484b702530106e85";
String city = "Palo Alto";
String countryCode = "US";
String jsonBuffer;
double TWeather;
double HWeather;
double PWeather;

int resetCounter = 0;


InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);                 //InfluxDB client instance with preconfigured InfluxCloud certificate

Point sensor("Upper Table");   


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
  String serverPath = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "," + countryCode + "&APPID=" + openWeatherMapApiKey;
  jsonBuffer = httpGETRequest(serverPath.c_str());
  JSONVar myObject = JSON.parse(jsonBuffer);

  if (JSON.typeof(myObject) == "undefined") {
        Serial.println("Parsing input failed!");
        resetCounter += 1;
        return;
      }

  T = tempSensor.readTempC();
  TWeather = (double) myObject["main"]["temp"];
  TWeather = TWeather - 273.15; //convert to celcius
  HWeather = (double) myObject["main"]["humidity"];
  PWeather = (double) myObject["main"]["pressure"];
  PWeather = PWeather/68.95; //convert to PSI

  // Check if any reads failed and exit early (to try again).
  if (isnan(T)) {
    Serial.println(F("Failed to read from temp sensor!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(TWeather)) {
    Serial.println(F("Failed to read weather T!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(HWeather)) {
    Serial.println(F("Failed to read weather H!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  if (isnan(PWeather)) {
    Serial.println(F("Failed to read weather P!"));
    delay(100);
    resetCounter += 1;
    return;
  }
  Serial.println("T");
  Serial.println(T);
  Serial.println("T Outside");
  Serial.println(TWeather);
  Serial.println("H Outside");
  Serial.println(HWeather);
  Serial.println("P Outside");
  Serial.println(PWeather);

  sensor.clearFields();
  sensor.addField("T", T );
  sensor.addField("Outside T", TWeather );
  sensor.addField("Outside H", HWeather );
  sensor.addField("Outside P", PWeather );


  if (WiFi.status() != WL_CONNECTED)  {                                //Check WiFi connection and reconnect if needed
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

String httpGETRequest(const char* serverName) {
  WiFiClient client;
  HTTPClient http;
    
  // Your Domain name with URL path or IP address with path
  http.begin(client, serverName);
  
  // Send HTTP POST request
  int httpResponseCode = http.GET();
  
  String payload = "{}"; 
  
  if (httpResponseCode>0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  // Free resources
  http.end();

  return payload;
}
