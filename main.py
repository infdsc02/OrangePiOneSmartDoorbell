from smartdoorbell import SmartDoorbell

if __name__ == '__main__':
    with SmartDoorbell() as smart_doorbell:
        smart_doorbell.loop()