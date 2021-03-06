#!/usr/bin/python
from curses.ascii import isdigit
import serial
import time
import os

def is_floatvalue(s):
   try:
      float(s)
      return True
   except ValueError:
      return False


inst = serial.Serial(port='/dev/ttyUSB0',
			baudrate=9600,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=1)

if inst.isOpen():
   inst.close()
   inst.open()

inst.write(':CONFigure:VOLTage\r')

try:
   while True:
#      inst.write(':MEASure:VOLTage?\r')
 #     inst.write(':MEASure:CHARge?\r')
      inst.write(':MEASure:CURRent?\r') 
      data = inst.read(50)
#      print(data)

      response = data.split(",")
      #could make some below variables for future
      if is_floatvalue(response[0]):
         value=float(response[0])*(1000000000000.)
         dbwrite = "influx -execute \'insert fc,tag=cross value={}\' -database=db".format(value)
      else:
         time.sleep(1)
      
      os.system(dbwrite)
      #print("{:.0f}".format(time.time()), response[0])
except KeyboardInterrupt:
   inst.close()
   pass

#def query(command):
#   inst.write(command)
#   out =''
#   out += inst.read(50)
#   return out

#def current(self):
#   command = ":MEASure:CURRent?" + "\r"
#   value = query(command)

# influx write based on this
#    databaseStr.Form("influx -execute \'insert %s,%s value=%f\' -database=%s", seriesName.Data(), tag.Data(), value, databaseName.c_str());
#     system(databaseStr.Data());
