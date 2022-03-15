import serial,time,os,can
if __name__ == '__main__':
    dati=0
    print('Running. Press CTRL-C to exit.')
    bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=125000)
    try:
        with serial.Serial("/dev/ttyUSB1", 115200, timeout=1) as arduino:
            if arduino.isOpen():
                for msg in bus:
                    dati=int.from_bytes(msg.data, byteorder='big', signed=False)
                    print(f"id: {msg.arbitration_id:X}")
                    print(f"Invio i dati ricevuti : {dati}")
                    arduino.write("{}".format(dati).encode('utf-8'))
    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught.")

