//Libraries
#include <Wire.h>                       // Used to establish serial communication on the I2C bus
#include <SparkFun_TMP117.h>            // Used to send and recieve specific information from our sensor
#include <SparkFun_Qwiic_Humidity_AHT20.h>
#include <SparkFun_MicroPressure.h> 

//Sensors
TMP117 tempSensor;
AHT20 humiditySensor;
SparkFun_MicroPressure mpr;

// Initial setup script
void setup()
{
  Wire.begin();
  Serial.begin(115200);    // Start serial communication at 115200 baud
  Wire.setClock(400000);   // Set clock speed to be the fastest for better communication (fast mode)

  // check connections of all sensors
  if (humiditySensor.begin() == false)
  {
    Serial.println("AHT20 not detected. Please check wiring. Freezing.");
    while (1);
  }
  Serial.println("AHT20 acknowledged.");


  if (tempSensor.begin() == false)
  {
    Serial.println("TMP117 not detected. Please check wiring. Freezing.");
    while (1);
  }
  Serial.println("TMP117 acknowledged.");

  if (mpr.begin() == false)
  {
    Serial.println("Micropressure Sensor not detected. Please check wiring. Freezing.");
    while (1);
  }
  Serial.println("Micropressure Sensor acknowledged.");

}
 
void loop()
{
  {
    float T = tempSensor.readTempC();
    float H = humiditySensor.getHumidity();
    float P = mpr.readPressure();

    Serial.println(String("Temperature: ")+T);
    Serial.println(String("Humidity: ")+H);
    Serial.println(String("Pressure: ")+P);

    delay(50); // slow the data aquisition time down a bit, 20Hz
  }
}
