import serial

serialPort = ""

def port():
    global serialPort
    serialPort = serial.Serial(port="dev/ttyUSB0", baudrate=115200, timeout=1)
    serialPort.write(str(10).encode('Ascii'))
    for i in range(10):
        
        serialString = serialPort.readline()
        data = str(serialString.decode('Ascii'))
        print(data)

    # serialPort.close()
    print("port closed")

port()
serialPort.close()
serialPort = serial.Serial(port="dev/ttyUSB0", baudrate=115200, timeout=1)
print(serialPort)