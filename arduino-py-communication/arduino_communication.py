import serial,time,os
if __name__ == '__main__':
    print('Running. Press CTRL-C to exit.')
    FIFO = 'myfifo'
    with open(FIFO) as fifo:
        with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
            time.sleep(0.1) #wait for serial to open
            if arduino.isOpen():
                try:
                    while True:
                    # while arduino.inWaiting()==0: pass
                        #if  arduino.inWaiting()>0:
                            #answer=str(arduino.readline())
                            #print(">>>{}".format(answer))

                        #while True:

                        for line in fifo:
                            arduino.write(line.encode())
                        #time.sleep(0.5) #wait for arduino to answer
                except KeyboardInterrupt:
                    print("KeyboardInterrupt has been caught.")

