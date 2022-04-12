# -*- coding: utf-8 -*-
"""
Created on Sep 1 2021

@author: shli

description: simple gui for plotting serial data
real time along with a table of measurements.


credits: much help from open-source code from
jagadish chandra bose research organization:
    https://www.jcbrolabs.org/
"""
import sys
import time
import numpy as np
import serial


from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import tkinter as tk
from functools import partial

# Connect to serial device

#if not ArduinoUnoSerial.isOpen():
  #  ArduinoUnoSerial.open()
#print('com6 is open', ArduinoUnoSerial.isOpen())
  
ArduinoUnoSerial = serial.Serial('com7',115200)       #Create Serial port object called ArduinoUnoSerialData time.sleep(2)                                                             #wait for 2 secounds for the communication to get established

# plotting vairables
num = 200  #-- number of points to plot at a given time

tact_data = [] # -- tempertaure data array for plot
pact_data =[]  # -- pressure data to plot


y_max = 15.8
y_min = 14.6
cond_array = [False]


def getdata():
    a=ArduinoUnoSerial.readline().decode('utf-8').rstrip()
    b=ArduinoUnoSerial.readline().decode('utf-8').rstrip()
        
    if (a[0:11]=="Temperature")& (b[0:8]=="Pressure"):
            T=float(a[13:18]);
            P=float(b[10:16]);
            
         
    elif (a[0:8]=="Pressure")& (b[0:11]=="Temperature"):
            T=float(b[13:18]);
            P=float(a[10:16]);

    else:        
            T=0.0
            P=0.0
            
    return T,P 


class Sensor_data():
    def __init__(self,name):
        
            self.root = tk.Tk()
            self.root.title('Serial data real-time plot')
            self.root.configure()
            self.root.geometry("1500x1000") # set the window size
            
            self.figFrame = tk.LabelFrame(self.root, text = "Pressure plot", padx = 5, pady = 5)
        
            self.name = name
            self.num=200
            self.y_min = 13 
            self.y_max = 15
            self.cond=False
            
            
            # Read in serial data:
            if self.name == "Pressure":
                self.y = getdata()[1]
                print(self.y)
            elif self.name =="Temperature":
                self.y = getdata()[0]
            
            
            self.y_data=[]
            self.y_value_array=[]
            
            # Prepare figure
 
            self.figFrame.grid(row = 0, column = 1, rowspan = 4)

            self.fig = Figure(figsize = (10, 2.5));
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.figFrame)  # A tk.DrawingArea.
           

            # canvas.get_tk_widget().place(x = 295,y=5, width = 700,height = 300)
            self.canvas.get_tk_widget().grid(row = 0, column = 0, columnspan = 2)
            
            
            
            self.ax = self.fig.add_subplot(111)
            self.ax.set_title('Pressure monitor');
            self.ax.set_xlabel('')
            self.ax.set_ylabel('Pressure (PSI)')
            self.ax.set_xlim(0,self.num)
            self.ax.set_ylim(self.y_min, self.y_max)
            self.ax.set_xticklabels([])
            self.y_line = self.ax.plot([],[],color = 'darkorange', label = "Pressure", linewidth = 1.2)
            self.ax.grid()
            self.ax.legend()
            self.canvas.draw()
            
            
            
            #------create measurement table object on GUI----------
            self.measFrame = tk.LabelFrame(self.root, text = "Measurements")
            self.measFrame.grid(row = 0, column = 0)
            # add measurement types and position on grid

            self.measurement_name = [self.name]

            self.measurement_label_array = []
            self.measurement_value_array = []

            self.measurement_label = tk.Label(self.measFrame, text = self.measurement_name)
            self.measurement_label.grid(row = 1, column = 0)


            self.measurement_value = tk.Label(self.measFrame, text = self.y, width = 20)
            self.measurement_value.grid(row = 1, column = 1)


            self.start = tk.Button(self.figFrame, text = "Start", font = ('calbiri',12),command = self.plot_start)
            self.start.grid(row =  1, column = 0)

            self.stop = tk.Button(self.figFrame, text = "Stop", font = ('calbiri',12), command =  self.plot_stop)
            self.stop.grid(row = 1, column = 1)

              

            # toolbar = NavigationToolbar2Tk(canvas, root)
            # toolrbar.grid(row = 0, column = 2)
            # toolbar.update()
            # canvas.get_tk_widget().pack()

            #----------create button---------

            # kill button
            self.kill = tk.Button(master=self.root, text="Quit", command=self._quit)
            self.kill.grid(row = 4, column = 1)


            # user input graph size
            self.axismodFrame = tk.LabelFrame(self.root, text = "Modify Axes", padx = 5, pady = 5)
            self.axismodFrame.grid(row = 3, column = 0)

            self.min_label =  tk.Label(self.axismodFrame, text = "Min",fg="black", width=10, height=3)
            self.max_label =  tk.Label(self.axismodFrame, text = "Max",fg="black", width=10, height=3)

            self.min_label.grid(row = 0, column = 0)
            self.max_label.grid(row = 0, column = 1)

            self.min_entry = tk.Entry(self.axismodFrame)
            self.max_entry = tk.Entry(self.axismodFrame)

            self.root.update();

            self.min_entry.grid(row = 1, column = 0)
            self.max_entry.grid(row = 1, column = 1)




            self.axis_modify_button = tk.Button(master = self.axismodFrame, text = "Modify y-axis", command = self.update_y)
            self.axis_modify_button.grid(row = 3, column = 0, columnspan = 2)

            
           
            
            
        
    def plot_data(self):
        
        # Read in serial data:
        if self.name == "Pressure":
            self.y = getdata()[1]
      
        elif self.name =="Temperature":
            self.y = getdata()[0]
            
        
        self.measurement_value.config(text=self.y)
            #####-- update plot with new data

        if (self.cond == True):

                    if(len(self.y_data) < self.num):
                       
                        self.y_data.append(self.y)
                        
                    else:
                        self.y_data[0:num-1] = self.y_data[1:num]
                        
                        self.y_data[num-1] =self.y
                        
                    #print(tact_data)
                  
                    self.y_line[0].set_xdata(np.arange(0,len(self.y_data)))
                    
                    self.y_line[0].set_ydata(self.y_data)
                

                    self.ax.set_ylim(self.y_min, self.y_max)
                    self.ax.set_ylim(self.y_min, self.y_max)
                    self.canvas.draw()
                    
        self.root.after(20,self.plot_data)             
            
    def update_y(self):
            
            self.y_min = float(self.min_entry.get())
            self.y_max = float(self.max_entry.get())
            
            
    def plot_start(self):
            print('start')
            self.cond = True
            ###s.reset_input_buffer()

    def plot_stop(self):
            self.cond = False     
            
  
            



          
    def _quit(self):
          
                self.root.quit()     # stops mainloop
                self.root.destroy()  # this is necessary on Windows to prevent
                                # Fatal Python Error: PyEval_RestoreThread: NULL tstate
                
                ArduinoUnoSerial.close()
###########################################
#----------- main gui code ---------------#
###########################################
# Insantiate sensor data object

#------create Plot object on GUI----------




PD=Sensor_data("Pressure")
PD.root.after(20,PD.plot_data())
PD.root.mainloop()


