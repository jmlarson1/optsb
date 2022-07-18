#!/usr/bin/python
import serial
import time

inst = serial.Serial(port='/dev/ttyUSB0',
			baudrate=9600,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=5)

if inst.isOpen():
   inst.close()
   inst.open()

inst.write(':CONFigure:VOLTage\r')

try:
   while True:
#      inst.write(':MEASure:VOLTage?\r')
      inst.write(':MEASure:CHARge?\r')
#      inst.write(':MEASure:CURRent?\r') 
      data = inst.read(50)
#      print(data)

      response = data.split(",")
      print("{:.0f}".format(time.time()), response[0])
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
