#!/usr/bin/python
from curses.ascii import isdigit
from socket import timeout
import serial
import serial.tools.list_ports
import time
import os

readtime=0.5 #how often to query in seconds

def is_floatvalue(s):
   try:
      float(s)
      return True
   except ValueError:
      return False

ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

if '232USB9M' in desc:
    keit_port = port

# can use below : port='/dev/ttyUSB0' or any other valid number
inst = serial.Serial(keit_port,
	             baudrate=9600,
		     bytesize=serial.EIGHTBITS,
		     parity=serial.PARITY_NONE,
	             stopbits=serial.STOPBITS_ONE,
		     timeout=readtime)

if inst.isOpen():
   inst.close()
   inst.open()

print("Connected, waiting 5 seconds before starting reads...")
time.sleep(5)

# placing Model 6485 in a “one-shot” measurement mode
inst.write(str.encode(':CONFigure:CURR:DC\r'))

print("reading...")
try:
   while True:
#      inst.write(':MEASure:VOLTage?\r')
#      inst.write(':MEASure:CHARge?\r')
#      inst.write(str.encode(':MEASure:CURRent?\r'))

# we do not need to use :MEASure command here, since configuration was done previously
      inst.write(str.encode(':READ?\r'))
      data = inst.read(60)
#      print(data)

      response = data.split(b',')
      current = response[0].decode()

#could make some below variables for future
      if is_floatvalue(current[:-1]) and current[-1]=='A':
          value=float(current[:-1])*(1000000000000.)
          dbwrite = "influx -execute \'insert fc,tag=cross value={}\' -database=db".format(value)
          os.system(dbwrite)
          print("{:.1f} {:.8f}".format(time.time(), value))
      else:
          print("something wrong with data, waiting...")
          time.sleep(readtime)
except KeyboardInterrupt:
   inst.close()
   pass

# influx write based on this
#    databaseStr.Form("influx -execute \'insert %s,%s value=%f\' -database=%s", seriesName.Data(), tag.Data(), value, databaseName.c_str());
#     system(databaseStr.Data());
