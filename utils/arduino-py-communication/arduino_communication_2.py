import time

import can
import serial

startMarker = "<"
endMarker = ">"
dataStarted = False
dataBuf = ""
messageComplete = False

# ========================
# ========================
# the functions


def setupSerial(baudRate, serialPortName):

    global serialPort

    serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=0, rtscts=True)  # type: ignore

    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))

    waitForArduino()


# ========================


def setupCan(bustype, channel, bitrate):

    global bus

    bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)  # type: ignore

    print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")


# ========================


def sendToArduino(stringToSend):

    # this adds the start- and end-markers before sending
    # global startMarker, endMarker, serialPort
    #
    # stringWithMarkers = (startMarker)
    # stringWithMarkers += stringToSend
    # stringWithMarkers += (endMarker)
    #
    # serialPort.write(stringWithMarkers.encode('utf-8')) # encode needed for Python3

    print(f"Sending {stringToSend}")
    serialPort.write(stringToSend.encode("utf-8"))  # encode needed for Python3


# ==================


def recvLikeArduino():

    # global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete
    #
    # if serialPort.inWaiting() > 0 and messageComplete == False:
    #     x = serialPort.read().decode("utf-8") # decode needed for Python3
    #
    #     if dataStarted == True:
    #         if x != endMarker:
    #             dataBuf = dataBuf + x
    #         else:
    #             dataStarted = False
    #             messageComplete = True
    #     elif x == startMarker:
    #         dataBuf = ''
    #         dataStarted = True
    #
    # if (messageComplete == True):
    #     messageComplete = False
    #     return dataBuf
    # else:
    #     return "XXX"

    global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete

    x = ""

    while serialPort.inWaiting() > 0:
        x += serialPort.read().decode("utf-8")  # decode needed for Python3

    return x


# ==================


def waitForArduino():

    # wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded

    print("Waiting for Arduino to reset")

    msg = ""
    while msg.find("Arduino is ready") == -1:
        msg = recvLikeArduino()
        if not (msg == "XXX"):
            print(msg)


# ====================


def readFromCan():

    global bus

    return [int.from_bytes(x.data, byteorder="big", signed=False) for x in bus]


# ====================
# ====================
# the program


setupSerial(115200, "/dev/ttyUSB1")
setupCan("socketcan", "can0", 12500)
prevTime = time.time()
while True:
    # check for a reply
    arduinoReply = recvLikeArduino()
    if not (arduinoReply == ""):
        print("Time %s  Reply %s" % (time.time(), arduinoReply))

        # send a message at intervals
    if time.time() - prevTime > 1.0:
        for data in readFromCan():
            sendToArduino(data)

        prevTime = time.time()
