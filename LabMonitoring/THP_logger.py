# imports
from time import sleep, strftime, time
from datetime import datetime
import serial
import sys, os
import matplotlib.pyplot as plt
import numpy as np



RATE = 10
COMPORT = 'COM7' #EDIT
SECS_IN_DAY = 60*60*24
ENTRIES_PER_DAY = int(SECS_IN_DAY/RATE)
DAYS = 2
ENTRIES = int(ENTRIES_PER_DAY*DAYS)
FILE = "SensorData.csv"
errCount = 0  # counts how many errors have been thrown
threshold = 100  # stops program if too many errors are thrown
TIME_TO_COLLECT = 18

def collectData():
  
  df = pd.read_csv(os.getcwd() + "//" + FILE)  # load up full data
  yesterday_df = df.iloc[-ENTRIES:].reset_index(drop=True)  # data frame with yesterdays data
  fs = 17
  ticks = 10
  fig, axe = plt.subplots(3, 1, figsize=(12,15))


  axe[0].plot(yesterday_df['Temperature (C)'])
  axe[0].set_title(f"{yesterday_df.iloc[0]['Date']} to {yesterday_df.iloc[-1]['Date']}", fontsize=17)
  axe[0].set_ylabel("Temperature (C)", fontsize=fs)
  plt.locator_params(axis='x', nbins=ticks)
  axe[0].tick_params(axis='both', labelsize=fs-3, direction='in', width=3, length=6 )
  axe[0].set_xticks([])

  data = list(yesterday_df["Temperature (C)"])
  minTemp = min(data)
  maxTemp = max(data)

  # axe[0].axvspan(0, int(3*60*60/RATE), alpha=0.2)
  # axe[0].axvspan(int(12*60*60/RATE), int(27*60*60/RATE), alpha=0.2)
  # axe[0].axvspan(int(36*60*60/RATE), len(data), alpha=0.2)
  axe[0].text(ENTRIES*1.1, maxTemp, f'Max Temp: {maxTemp} C', fontsize=20)
  axe[0].text(ENTRIES*1.1, maxTemp-0.1, f'Min Temp:  {minTemp} C', fontsize=20)
  axe[0].text(ENTRIES*1.1, maxTemp-0.2, f'Avg Temp:  {round(np.average(data),2)} C', fontsize=20)
  axe[0].text(ENTRIES*1.1, maxTemp-0.3, f'StDev T:      {round(np.std(data),2)} C', fontsize=20)
  axe[0].axhline(np.average(data), linestyle = '--', color = 'green')

  # Humidity

  axe[1].plot(yesterday_df['Humidity'])
  axe[1].set_ylabel("Humidity", fontsize=fs)

  plt.locator_params(axis='x', nbins=ticks)
  axe[1].tick_params(axis='both', labelsize=fs-3, direction='in', width=3, length=6 )
  axe[1].set_xticks([])

  data = list(yesterday_df["Humidity"])
  minHum = min(data)
  maxHum = max(data)

  # axe[1].axvspan(0, int(3*60*60/RATE), alpha=0.2)
  # axe[1].axvspan(int(12*60*60/RATE), int(27*60*60/RATE), alpha=0.2)
  # axe[1].axvspan(int(36*60*60/RATE), len(data), alpha=0.2)
  axe[1].text(ENTRIES*1.1, maxHum, f'Max Hum: {maxHum} C', fontsize=20)
  axe[1].text(ENTRIES*1.1, maxHum-1.5, f'Min Hum:  {minHum} C', fontsize=20)
  axe[1].text(ENTRIES*1.1, maxHum-3, f'Avg Hum:  {round(np.average(data),2)} C', fontsize=20)
  axe[1].text(ENTRIES*1.1, maxHum-4.5, f'StDev H:      {round(np.std(data),2)} C', fontsize=20)
  axe[1].axhline(np.average(data), linestyle = '--', color = 'green')

  # Pressure

  axe[2].plot(yesterday_df['Pressure (PSI)'])
  axe[2].set_xlabel("Date/Time", fontsize=fs)
  axe[2].set_ylabel("Pressure (PSI)", fontsize=fs)

  step = int(ENTRIES/ticks)
  plt.locator_params(axis='x', nbins=ticks)
  axe[2].set_xticklabels([str(yesterday_df.iloc[i*step]["Date"])[10:] for i in range(ticks)], rotation=45, fontsize=fs-3)

  axe[2].tick_params(axis='both', labelsize=fs-3, direction='in', width=3, length=6 )


  data = list(yesterday_df["Pressure (PSI)"])
  minPress = min(data)
  maxPress = max(data)

  # axe[2].axvspan(0, int(3*60*60/RATE), alpha=0.2)
  # axe[2].axvspan(int(12*60*60/RATE), int(24*60*60/RATE), alpha=0.2)
  # axe[2].axvspan(int(36*60*60/RATE), int(48*60*60/RATE), alpha=0.2)
  axe[2].text(ENTRIES*1.1, maxPress, f'Max Press: {maxPress} C', fontsize=20)
  axe[2].text(ENTRIES*1.1, maxPress-0.01, f'Min Press:  {minPress} C', fontsize=20)
  axe[2].text(ENTRIES*1.1, maxPress-0.02, f'Avg Press:  {round(np.average(data),2)} C', fontsize=20)
  axe[2].text(ENTRIES*1.1, maxPress-0.03, f'StDev P:     {round(np.std(data),2)} C', fontsize=20)
  axe[2].axhline(np.average(data), linestyle = '--', color = 'green')


  fig.tight_layout()

  plt.savefig("Data//Data" + yesterday_df.iloc[0]['Date'][5:10] + "_" + yesterday_df.iloc[-1]['Date'][5:10] + ".png", bbox_inches='tight')
  yesterday_df.to_csv( "Data//Data" + yesterday_df.iloc[0]['Date'][5:10] + "_" + yesterday_df.iloc[-1]['Date'][5:10] + ".csv")

  plt.close()

ser = serial.Serial(COMPORT, 115200, timeout=2)  # sets active serial port and baud rate

ser.readline()
ser.readline()
ser.readline()  # pulls out board acknowledgement inputs

 # hour to collect plot data at
oldT = datetime.now().hour
with open(os.getcwd().replace('\\', '/') + '/' + FILE, "a") as log:    
  print('><><><><><><><><><><><><><><><')
  print('>---COLLECTING SENSOR DATA---<')
  print('><><><><><><><><><><><><><><><')
  print('Writing Data To: ' + filePath)
  while errCount < threshold:

    newT = datetime.now().hour  # checks if 6am has passed, if so, grab and plot the last two days of data
    if (newT == TIME_TO_COLLECT) and (oldT != newT):
      collectData()
    oldT = newT

    try:
      ser.reset_input_buffer()
      # ensures data is being collected in correct order, throws assertion error otherwise
      t = ser.readline()
      assert str(t)[2:13] == 'Temperature'

      h = ser.readline()
      assert str(h)[2:10] == 'Humidity'

      p = ser.readline()
      assert str(p)[2:10] == 'Pressure'

      temp = float(str(t).lstrip("b'Temperature: ").rstrip("\\r\\n'"))
      humidity = float(str(h).lstrip("b'Humidity: ").rstrip("\\r\\n'"))
      press = float(str(p).lstrip("b'Pressure: ").rstrip("\\r\\n'"))

      print(f"Temperature: {temp}")
      print(f"Humidity: {humidity}")
      print(f"Pressure: {press}")
      log.write("{0},{1},{2},{3}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(temp), str(humidity), str(press)))
    except (ValueError, AssertionError) as e:
      print(e)
      errCount += 1
      pass
    sleep(RATE)
    

  ser.close()     
    
