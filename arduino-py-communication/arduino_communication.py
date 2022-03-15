import serial,time,os,can
if __name__ == '__main__':
    print('Running. Press CTRL-C to exit.')
    FIFO = '../myfifo'
    try:
        bus = can.interface.Bus(bustype='seeedstudio', channel='can0', bitrate=125000)
        for msg in bus:
            print(f"{msg.arbitration_id:X}: {msg.data}")
        #with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
            #with open(FIFO) as fifo:
                #time.sleep(0.1) #wait for serial to open
                #if arduino.isOpen():
                    #for line in fifo:
                        #print("Invio :{}".format(line.encode()))
                        #arduino.write(5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught.")
