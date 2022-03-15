import serial,time,os
if __name__ == '__main__':
    print('Running. Press CTRL-C to exit.')
    FIFO = '../myfifo'
    try:
        with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
            with open(FIFO) as fifo:
                time.sleep(0.1) #wait for serial to open
                if arduino.isOpen():
                    for line in fifo:
                        print("Invio :{}".format(line.encode()))
                        arduino.write(5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught.")

