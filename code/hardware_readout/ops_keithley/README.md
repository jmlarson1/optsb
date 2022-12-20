Info / instructions from dan.

Hi Calem,
 
Attached is a directory containing the code. In order to build this all you have to do is set this directory as your current working directory, then type “make” on the command line (let me know if you see errors, I’m not 100% sure where or if dependencies are installed on your machine). It’s okay if you see a list of warnings, but it builds okay. You should then get a binary called “ATLAS_Native_Serial_Test”. To run it type “./ATLAS_Native_Serial_Test”. There is one one option (option 1). Type one on the command line followed by enter. It will prompt you for a serial port, for me this was port 0, but you can check by typing “ls /dev/ttyUSB*” on the command line to see what port the Keithley is using. It will then bring you back to the main screen, choose 1 again. It will prompt you with a command line. Listed below are the commands the Keithley will accept:

READ? = Get a reading from the Keithley
INIT = Initialize the device
SENS:CURR:RANG 2E-7, SENS:CURR:RANG 2E-4, SENS:CURR:RANG 2E-8, etc. = Change the range of current
SYST:PRESET = Reset
SYSTEM:CLEAR: Clear the System:
SENS:CURR:RANG:AUTO ON = Turn on auto Range
SENS:CURR:RANG:AUTO OFF = Turn off auto Range.
 
 
Let me know if you need any additional information. Also let me know if you would like a more Keithley specific/ user friendly program and I can make one.
 
Thank you,
Dan