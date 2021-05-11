#!/usr/local/bin/python3

import serial
import time
from datetime import datetime, date

SERIALPORT = "/dev/tty.usbserial-141340"
BAUDRATE = 38400

ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
ser.timeout = 3
#ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 3

initcmd='\n0'

timestring = "%s%02d%02d%02d%02d" % (
    str(datetime.now().year)[:2],
    datetime.now().month,
    datetime.now().day,
    datetime.now().hour,
    datetime.now().minute)
commandToSend = initcmd + '27' + timestring + '\r'

buffer=ser.read(ser.inWaiting())

print ("Writing: ",  commandToSend)
buffer=str(commandToSend).encode()
ser.write(buffer)
print(ser.read(ser.inWaiting()))
ser.close()
ser.open()
while True:
  buf=ser.inWaiting()
  if(buf > 0):
    print(ser.read_until('\r'))

ser.close()

