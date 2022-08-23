import can
import serial

# ========================


def setupSerial(baudRate, serialPortName):

    global serialPort

    serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=1)  # type: ignore

    print(f"Serial port {serialPortName} opened @{baudRate}")


# ========================


def setupCan(bustype, channel, bitrate):

    global bus

    bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)  # type: ignore

    print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")


# ========================


def sendToArduino(stringToSend):

    serialPort.write(f"{stringToSend}".encode("utf-8"))  # encode needed for Python3


# ==================


def recvLikeArduino():

    global serialPort

    data = serialPort.readline().decode("utf-8")

    if data != "":
        print(f"ESP> {data}")


# ==================


def readFromCan():

    global bus

    msg = bus.recv(timeout=0.5)

    if msg is not None:
        msg = int.from_bytes(msg.data, byteorder="big", signed=False)
        print(f"CAN> {msg}")

    return msg


# ====================

if __name__ == "__main__":

    print("Starting... press Ctrl+c to quit")
    setupSerial(115200, "/dev/ttyUSB0")
    setupCan("socketcan", "can0", 12500)
    while True:
        try:
            # Receive from serial
            recvLikeArduino()

            # Receive from can
            data = readFromCan()
            if data is not None:
                # Transmit to serial
                sendToArduino(data)
        except KeyboardInterrupt:
            print("Quitting...")
            break
