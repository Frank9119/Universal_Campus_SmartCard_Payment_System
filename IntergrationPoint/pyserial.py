import serial
import serial.tools.list_ports
import subprocess
from sudo import run_as_sudo



port1 = ""
def comPort():
    global port1
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print("Description: " + p.description)
        print("Name: " + p.name)
        print("Name: " + str(p.device) +":" + str(p.serial_number) + ":" + str(p.vid) +":>" + str(p.hwid)+ ":"+ str(p.product) +"<:"+ str(p.pid))

        if 'CH340' in p.description or '10C4:EA60' in p.hwid  or '1A86:7523' in p.hwid:
            print(p.description)
            print(p.device)
            port1 = str(p.device)
            # print(serial.Serial(p.device))
            print(' Hardware is Connected at Port', port1)

            try:
                cmd = "chmod 777 %s" % port1
                sudo_user = "root"
                print("Running Command")
                # run_as_sudo (sudo_user, cmd)
                subprocess.run(["sudo", "chmod", "777", "%s" % port1])
                # subprocess.run(["ls", "-l"])
                print("Command run Succesful")

            except:
                print("Command run Unsuccesful")
                print("sudo", "chmod", 777, "%s" % port1)
        else:
            port1 = ""
            print(port1, 'No Hardware is Connected')


    return port1

# sudo chmod 777 /dev/ttyUSB0