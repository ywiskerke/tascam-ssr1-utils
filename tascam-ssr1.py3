#!/usr/local/bin/python3

import serial
from time import sleep
from datetime import datetime, date

ser = serial.Serial("/dev/tty.usbserial-141340",19200)

ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
ser.timeout = 0
#ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 0

sendCmd=b''
sendVal=b''
retCmd=b''
retVal=b''
trackElapsed=''
trackRemain=''
mediaElapsed=''
mediaRemain=''
mechStat=''
debug = False

timestring = "%s%02d%02d%02d%02d" % (
    str(datetime.now().year)[:2],
    datetime.now().month,
    datetime.now().day,
    datetime.now().hour,
    datetime.now().minute)

# First set Time on Tascam
sendCmd=b'027'
sendVal=timestring.encode()

def ClockDataReturn(val):
  clockText="%d/%d/%d %d:%d:%d:%d" % (
      val[0:1],  # Year
      val[2:3],  # Month
      val[4:5],  # Day
      val[6:7],  # Hours
      val[8:9],  # Minutes
      val[10:11] # Seconds
      )
  return clockText

def MechaStatReturn(val):
  MechStatusText = {
    b'00' : "No Media",
    b'10' : "Stopped",
    b'11' : "Play",
    b'12' : "Ready On",
    b'80' : "Monitor",
    b'81' : "Record",
    b'82' : "Record Ready",
    b'83' : "Information Writing"
    }
  mechStat=MechStatusText[val]
  return mechStat

def TrackNoReturn(val):
  trackNo = "%c%c%c%c" % (
      chr(val[4]),
      chr(val[5]),
      chr(val[2]),
      chr(val[3]))
  eomStat=val[0:2]
  if (trackNo!="0000"):
    sendCmd=b'059'
    sendVal=val[2:6]
  if debug:
    print("Track: " + trackNo)
  return trackNo

def CurTrackInfoReturn(val):
  trackNo= "%c%c%c%c" % (
      chr(val[2]),
      chr(val[3]),
      chr(val[0]),
      chr(val[1]))
  trackTotalTime= "min: %c%c%c%c sec:%c%c fr:%c%c" % (
      chr(val[7]),  # 1000s Min
      chr(val[6]),  # 100s  Min
      chr(val[4]),  # 10s   Min
      chr(val[5]),  # 1s    Min
      chr(val[8]),  # 10s   Sec
      chr(val[9]),  # 1s    Sec
      chr(val[10]), # 10s  Frames
      chr(val[11])) # 1s   Frames
  if debug:
    print('Tr#' + trackNo + ' Total:' + trackTotalTime)
  return trackTotalTime

def NameReturn(val):
  global debug
  trackNo= "%c%c%c%c" % (
      chr(val[2]), # 1000s trackno
      chr(val[3]), # 100s  trackno
      chr(val[0]), # 10s   trackno
      chr(val[1])) # 1s    trackno
  trackName = val[4:]
  if debug:
    print(trackNo + ' ' + str(trackName,"utf-8"))
  return trackName

def stub(val):
  return ""

returnText = {
    b'8F' : "INFORMATION RETURN",
    b'97' : "FLASH LOAD ACKNOWLEDGE",
    b'A0' : "AUTO CUE LEVEL RETURN", 
    b'A1' : "AUTO TRACK LEVEL RETURN",
    b'A5' : "PITCH DATA RETURN",
    b'A6' : "AUTO TRACK TIME RETURN",
    b'A7' : "CLOCK DATA RETURN",
    b'A8' : "SYNC REC LEVEL RETURN",
    b'AD' : "KEY CONTROL DATA RETURN",
    b'B0' : "AUTO CUE SELECT RETURN",
    b'B1' : "AUTO TRACK RETURN",
    b'B2' : "EOM TRACK TIME RETURN",
    b'B3' : "EOM MEDIA TIME RETURN",
    b'B5' : "PITCH CONTROL SELECT RETURN",
    b'B6' : "AUTO READY SELECT RETURN",
    b'B7' : "REPEAT SELECT RETURN",
    b'B8' : "SYNC REC SELECT RETURN",
    b'BA' : "INCR PLAY SELECT RETURN",
    b'BD' : "KEY CONTROL SELECT RETURN",
    b'CC' : "REMOTE/LOCAL SELECT RETURN",
    b'CE' : "PLAY MODE RETURN",
    b'D0' : "MECHA STATUS RETURN",
    b'D5' : "TRACK No. STATUS RETURN",
    b'D6' : "MEDIA STATUS RETURN",
    b'D7' : "CURRENT TRACK INFORMATION RETURN",
    b'D8' : "CURRENT TRACK TIME RETURN",
    b'D9' : "NAME RETURN",
    b'DD' : "TOTAL TRACK No./TOTAL TIME RETURN",
    b'DE' : "PGM TOTAL TRACK No./TOTAL TIME RETURN",
    b'DF' : "KEYBOARD TYPE RETURN ",
    b'F0' : "ERROR SENSE REQUEST",
    b'F1' : "CAUTION SENSE REQUEST",
    b'F2' : "ILLEGAL STATUS",
    b'F4' : "POWER ON STATUS",
    b'F6' : "CHANGE STATUS",
    b'F8' : "ERROR SENSE RETURN",
    b'F9' : "CAUTION SENSE RETURN",
    b'FF' : "VENDER COMMAND RETURN",
  }

responseActionList = {
    b'8F' : ("INFORMATION RETURN", stub, None ),
    b'97' : ("FLASH LOAD ACKNOWLEDGE", stub, None ),
    b'A0' : ("AUTO CUE LEVEL RETURN", stub, None ),
    b'A1' : ("AUTO TRACK LEVEL RETURN", stub, None ),
    b'A5' : ("PITCH DATA RETURN", stub, None ),
    b'A6' : ("AUTO TRACK TIME RETURN", stub, None ),
    b'A7' : ("CLOCK DATA RETURN", ClockDataReturn, None ),
    b'A8' : ("SYNC REC LEVEL RETURN", stub, None ),
    b'AD' : ("KEY CONTROL DATA RETURN", stub, None ),
    b'B0' : ("AUTO CUE SELECT RETURN", stub, None ),
    b'B1' : ("AUTO TRACK RETURN", stub, None ),
    b'B2' : ("EOM TRACK TIME RETURN", stub, None ),
    b'B3' : ("EOM MEDIA TIME RETURN", stub, None ),
    b'B5' : ("PITCH CONTROL SELECT RETURN", stub, None ),
    b'B6' : ("AUTO READY SELECT RETURN", stub, None ),
    b'B7' : ("REPEAT SELECT RETURN", stub, None ),
    b'B8' : ("SYNC REC SELECT RETURN", stub, None ),
    b'BA' : ("INCR PLAY SELECT RETURN", stub, None ),
    b'BD' : ("KEY CONTROL SELECT RETURN", stub, None ),
    b'CC' : ("REMOTE/LOCAL SELECT RETURN", stub, None ),
    b'CE' : ("PLAY MODE RETURN", stub, None ),
    b'D0' : ("MECHA STATUS RETURN", MechaStatReturn, None ),
    b'D5' : ("TRACK No. STATUS RETURN", TrackNoReturn, None ),
    b'D6' : ("MEDIA STATUS RETURN", stub, None ),
    b'D7' : ("CURRENT TRACK INFORMATION RETURN", CurTrackInfoReturn, None ),
    b'D8' : ("CURRENT TRACK TIME RETURN", stub, None ),
    b'D9' : ("NAME RETURN", NameReturn, None ),
    b'DD' : ("TOTAL TRACK No./TOTAL TIME RETURN", stub, None ),
    b'DE' : ("PGM TOTAL TRACK No./TOTAL TIME RETURN", stub, None ),
    b'DF' : ("KEYBOARD TYPE RETURN ", stub, None ),
    b'F0' : ("ERROR SENSE REQUEST", stub, None ),
    b'F1' : ("CAUTION SENSE REQUEST", stub, None ),
    b'F2' : ("ILLEGAL STATUS", stub, None ),
    b'F4' : ("POWER ON STATUS", stub, None ),
    b'F6' : ("CHANGE STATUS", stub, None ),
    b'F8' : ("ERROR SENSE RETURN", stub, None ),
    b'F9' : ("CAUTION SENSE RETURN", stub, None ),
    b'FF' : ("VENDER COMMAND RETURN", stub, None ),
  }

while True:
  if (sendCmd != b''):
    cmd=b'\n' + sendCmd + sendVal + b'\r'
    ser.write(cmd)
    sendCmd=b''
    sendVal=b''

  sleep(0.2)
  if (ser.inWaiting() != 0):
    response=ser.read(size=ser.inWaiting())
    retCmd=response[2:4]
    retVal=response[4:len(response)-1]
    print(returnText[retCmd])
    if debug:
      print('cmd:' + str(retCmd))
      print('val:' + str(retVal))

    # CLOCK DATA PRESET RETURN
    if (retCmd==b'A7'):
      print(ClockDataReturn(retVal))

    # MECHA STATUS RETURN
    if (retCmd==b'D0'):
      if (retVal==b'11'):
        sendCmd=b'055' # TRACK NO RETURN
      if (retVal==b'12'):
        sendCmd=b'055' # TRACK NO RETURN
      print (MechaStatReturn(retVal))

    # Track No. RETURN
    if (retCmd==b'D5'):
      trackNo=TrackNoReturn(retVal)
      if (trackNo!="0000"):
        sendCmd=b'059'
        sendVal=retVal[2:6]
      print(trackNo)

    # CURRENT TRACK INFORMATION RETURN
    if (retCmd==b'D7'):
      #print(CurTrackInfoReturn(retVal))
      print(returnText(retVal))

    # CURRENT TRACK TIME RETURN
    if (retCmd==b'D8'):
      timeVal = "min: %c%c%c%c sec:%c%c fr:%c%c" % (
          chr(retVal[5]),  # 1000s Min
          chr(retVal[4]),  # 100s  Min
          chr(retVal[2]),  # 10s   Min
          chr(retVal[3]),  # 1s    Min
          chr(retVal[6]),  # 10s   Sec
          chr(retVal[7]),  # 1s    Sec
          chr(retVal[8]),  # 10s  Frames
          chr(retVal[9]))  # 1s   Frames
      if (retVal[0:2]==b'00'):
        trackElapsed=timeVal
      else:
        if (retVal[0:2]==b'01'):
          trackRemain=timeVal
        else:
          if (retVal[0:2]==b'02'):
            mediaElapsed=timeVal
          else:
            if (retVal[0:2]==b'03'):
              mediaRemain=timeval

    # NAME RETURN
    if (retCmd==b'D9'):
      print(NameReturn(retVal))

    if (retCmd==b'F2'):
      print('ILLEGAL [F2]')

    # Change Status F6
    if (retCmd==b'F6'):
      if (retVal==b'00'):
        sendCmd=b'055' # Call TrackNumber Return

      if (retVal==b'03'):
        sendCmd=b'050' # Call Mech Status Return

    retCmd=b''
    retVal=b''

