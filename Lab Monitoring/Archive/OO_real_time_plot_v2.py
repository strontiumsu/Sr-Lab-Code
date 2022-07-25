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



tact_data = [] # -- tempertaure data array for plot
pact_data =[]  # -- pressure data to plot


y_max = 15.8
y_min = 14.6
cond_array = [False]


def getdata():
    a=ArduinoUnoSerial.readline().decode('utf-8').rstrip()
    b=ArduinoUnoSerial.readline().decode('utf-8').rstrip()
    c=ArduinoUnoSerial.readline().decode('utf-8').rstrip()
        
    if (a[0:11]=="Temperature")& (b[0:8]=="Pressure")& (c[0:8]=="flowrate"):
            T=float(a[13:18]);
            P=float(b[10:16]);
            Q=float(c[10:16]);
            
         
    elif (a[0:8]=="Pressure")& (b[0:8]=="Flowrate")&(c[0:11]=="Temperature"):
            P=float(a[10:16]);
            Q=float(b[10:16]);
            T=float(c[13:18]);
            
    elif  (a[0:8]=="Flowrate")&(b[0:11]=="Temperature")&(c[0:8]=="Pressure"):
            Q=float(a[10:16]);
            P=float(b[10:16]);
            T=float(c[13:18]);         

    else:        
            T=0.0
            P=0.0
            Q=0.0
            
    return T,P,Q 


class Sensor_data():
    def __init__(self,name,units,root,figFrame,row=0,y_min=0,y_max=100,num=150):
        
            self.root = root
            self.name = name
            self.units = units
            self.row=row
            
            self.figFrame=figFrame
           
            self.fig = Figure(figsize = (10, 2.5));            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.figFrame)  # A tk.DrawingArea.
        
            self.num=num
            self.y_min = y_min 
            self.y_max = y_max
            self.cond=False
            
            # Read in serial data:
            if self.name == "Pressure":
                self.y = getdata()[1]
                print(self.y)
            elif self.name =="Temperature":
                self.y = getdata()[0]
            elif self.name =="Flowrate":
                self.y = getdata()[2]    
            
            
            self.y_data=[]
            self.y_value_array=[]
            
            # Prepare figure
 
            # canvas.get_tk_widget().place(x = 295,y=5, width = 700,height = 300)
            self.canvas.get_tk_widget().grid(row = 2*self.row, column = 0, columnspan = 2)
            
            self.ax = self.fig.add_subplot(111)
            self.ax.set_title(self.name+' monitor');
            self.ax.set_xlabel('')
            self.ax.set_ylabel(self.name+' ('+self.units+')')
            self.ax.set_xlim(0,self.num)
            self.ax.set_ylim(self.y_min, self.y_max)
            self.ax.set_xticklabels([])
            self.y_line = self.ax.plot([],[],color = 'darkorchid', label = self.name, linewidth = 2.0)
            self.ax.grid()
            self.ax.legend()
            self.canvas.draw()
            
            
            
            
            self.start = tk.Button(self.figFrame, text = "Start", font = ('calbiri',12),command = self.plot_start)
            self.start.grid(row =  2*self.row+1, column = 0)

            self.stop = tk.Button(self.figFrame, text = "Stop", font = ('calbiri',12), command =  self.plot_stop)
            self.stop.grid(row = 2*self.row+1, column = 1)
            
            
            #------create measurement table object on GUI----------
            self.measFrame = tk.LabelFrame(self.root, text = "Measurement")
            self.measFrame.grid(row = self.row, column = 0)
            # add measurement types and position on grid

            self.measurement_name = self.name+' ('+self.units+')'

            self.measurement_label_array = []
            self.measurement_value_array = []

            self.measurement_label = tk.Label(self.measFrame, text = self.measurement_name)
            self.measurement_label.grid(row = self.row, column = 0)
            

            self.measurement_value = tk.Label(self.measFrame, text = self.y, width = 20)
            self.measurement_value.grid(row = self.row, column = 1)
            


            # user input graph size
            self.axismodFrame = tk.LabelFrame(self.measFrame, text = "Modify Axes", padx = 0, pady = 0)
            self.axismodFrame.grid(row = self.row+1, column = 0,sticky="n")

            self.min_label =  tk.Label(self.axismodFrame, text = "Min",fg="black", width=10, height=3)
            self.max_label =  tk.Label(self.axismodFrame, text = "Max",fg="black", width=10, height=3)

            self.min_label.grid(row = self.row, column = 0)
            self.max_label.grid(row = self.row, column = 1)

            self.min_entry = tk.Entry(self.axismodFrame)
            self.max_entry = tk.Entry(self.axismodFrame)

            self.root.update();

            self.min_entry.grid(row = self.row+1, column = 0)
            self.max_entry.grid(row = self.row+1, column = 1)

            self.axis_modify_button = tk.Button(master = self.axismodFrame, text = "Modify y-axis", command = self.update_y)
            self.axis_modify_button.grid(row = self.row+2, column = 0, columnspan = 2,sticky="n")

            
    def plot_data(self):
        
        # Read in serial data:
        if self.name == "Pressure":
            self.y = getdata()[1]
      
        elif self.name =="Temperature":
            self.y = getdata()[0]
            
            
        elif self.name =="Flowrate":
            self.y = getdata()[2]    
            
        
        self.measurement_value.config(text=self.y)
            #####-- update plot with new data

        if (self.cond == True):

                    if(len(self.y_data) < self.num):
                       
                        self.y_data.append(self.y)
                        
                    else:
                        self.y_data[0:self.num-1] = self.y_data[1:self.num]
                        
                        self.y_data[self.num-1] =self.y
                        
                    #print(tact_data)
                  
                    self.y_line[0].set_xdata(np.arange(0,len(self.y_data)))
                    
                    self.y_line[0].set_ydata(self.y_data)
                

                    self.ax.set_ylim(self.y_min, self.y_max)
                    self.ax.set_ylim(self.y_min, self.y_max)
                    self.canvas.draw()
        
        #root.after(1,self.plot_data)
                      
            
    def update_y(self):
            
            self.y_min = float(self.min_entry.get())
            self.y_max = float(self.max_entry.get())
            
            
    def plot_start(self):
            print('start')
            self.cond = True
            ###s.reset_input_buffer()

    def plot_stop(self):
            self.cond = False     
def _quit():
          
                root.quit()     # stops mainloop
                root.destroy()  # this is necessary on Windows to prevent
                                # Fatal Python Error: PyEval_RestoreThread: NULL tstate
                
                ArduinoUnoSerial.close()
                

def on_closing():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    
    ArduinoUnoSerial.close()
                
class Sensor_data_plot:  
    
       def __init__(self,SD1,SD2,SD3):
           self.SD1=SD1
           self.SD2=SD2
           self.SD3=SD3
           
           
       def data_plot(self):   
            self.SD1.plot_data()
            self.SD2.plot_data()
            self.SD3.plot_data()
            root.after(1,self.data_plot)
           
            
            
            
###########################################
#----------- main gui code ---------------#
###########################################
# Insantiate sensor data object

#------create Plot object on GUI----------

root=tk.Tk()

root.title('Serial data real-time plot')
root.configure()
root.geometry("1500x1000") # set the window size


kill = tk.Button(master=root, text="Quit", command=_quit)
kill.grid(row = 4, column = 1)

figFrame = tk.LabelFrame(root, text = "Plots", padx = 5, pady = 5)
figFrame.grid(row = 0, column = 1, rowspan = 4)

#name,root,row,y_min,y_max,num

PD1=Sensor_data("Pressure","PSI",root,figFrame,row=0,y_min=11.5,y_max=14,num=400)
# kill button
PD2=Sensor_data("Temperature","C",root,figFrame,row=1,y_min=12,y_max=25,num=400)
PD3=Sensor_data("Flowrate","l/min",root,figFrame,row=2,y_min=0,y_max=25,num=400)


SDP=Sensor_data_plot(PD1, PD2,PD3)
root.after(1,SDP.data_plot)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()


