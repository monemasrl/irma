  GNU nano 5.4                                                                  arduino_communication.py                                                                            
import serial,time
if __name__ == '__main__':
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    while arduino.inWaiting()==0: pass
                    if  arduino.inWaiting()>0:
                      answer=str(arduino.readline())
                      print("---> {}".format(answer))
                      if answer=="start":
                       with open('binary_dump.log') as f:
                         for last_line in f:
                           pass
                         print(last_line)
                         arduino.write(last_line.encode())
                    #time.sleep(0.1) #wait for arduino to answer
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")


