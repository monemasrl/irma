import can, time

if __name__ == '__main__':
    bus = can.Bus(interface='socketcan', channel='can0') # type: ignore
    try:
        while True:
            message = can.Message(
                arbitration_id=123,
                is_extended_id=True,
                data=[0x11],
            )
            bus.send(message, timeout=0.2)
            print("Message 1 sent")
            time.sleep(2)
            message = can.Message(
                arbitration_id=123,
                is_extended_id=True,
                data=[0x09],
            )
            bus.send(message, timeout=0.2)
            print("Message 2 sent")
            time.sleep(2)

    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught.")
