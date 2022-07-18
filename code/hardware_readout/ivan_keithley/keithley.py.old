import visa
import time

rm = visa.ResourceManager()

keithley = rm.open_resource('GPIB0::16::INSTR')
keithley.write("FORM:ELEM READ")

fileName_path = '/Users/ivantol/Desktop/CENNS10_Work/keithley/'
fileName = fileName_path + time.strftime("%Y%m%d%H%M%S") + '_scan.txt'

print "********** creating file {} **********".format(fileName)

with open(fileName, 'a') as o:
     o.write('time' + '\t' + 'voltage' + '\n')
     o.close()

try:
   while True:
      with open(fileName, 'a') as o:
      	 voltage = keithley.query(":MEASure:VOLTage:DC?") # query(":MEASURE?") does work too
         o.write(str(time.time()) + '\t' + str(voltage))
         print time.time()
      time.sleep(5)
except KeyboardInterrupt:
   o.close()
   pass   