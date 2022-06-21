#!/usr/bin/python
import serial
import time
import Edwards_D379_driver

route = Edwards_D379_driver.Route()
gaude_read = Edwards_D379_driver.EdwardsD397(route)

while 1:

   output1 = gaude_read.vacuum_g1()
   output2 = gaude_read.vacuum_g2()
   output3 = gaude_read.vacuum_Punits()
   output4 = gaude_read.vacuum_allg()
   
   print output1
   print output4
   time.sleep(1)
#   print output2
