from pyax12.connection import Connection
from pyax12 import *
import time
import RPi.GPIO as GPIO
import signal
import sys
#from subprocess import call

import socket

# Configuratie
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer
# Open webserver socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True)

GPIO.setwarnings(False)

gopen = 300
gclosed = 50

beneden = 1023
boven = 0

spdt = 100
spda = 25
spdg = 500
spdr = 100

dynashoulder = 61
dynaelbow = 3
dynatrans = 69
dynarot = 88
dynagrip = 2
motors = [dynashoulder, dynaelbow, dynatrans, dynarot, dynagrip]

smode = 0
tranlation = 1
power = 2
autonomous = 3
light = 4
vertical_rjoy = 5
horizontal_rjoy = 6
horizontal_ljoy = 7
vertical_ljoy = 8
rasp_onoff = 9
send_servo_data = 10

loop = True

time.sleep(0.1)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    loop = False
    serial_connection.close()
    s.shutdown(0)
    s.close()
    print('doei')
    sys.exit(0)




def test():

    
    s.bind((HOST, PORT))
    time.sleep(0.01)
    s.listen()
    time.sleep(0.01)

    while(True):
        signal.signal(signal.SIGINT, signal_handler)
        #print(f'Server listening on {HOST}:{PORT}')
        conn, addr = s.accept()
        #print(f'Connected by {addr}')
        
        txt = conn.recv(1024)
        txt2 = txt.decode()
        print(txt2)
        webdata = txt2.split(",")
        #print(webdata[vertical_ljoy])

#        time.sleep(1)
        if int(webdata[rasp_onoff]) == 1:
            time.sleep(1)
            print('De raspberry sluit nu af. Doei!')
            conn.send('Raspberry uit')
            conn.close()
            serial_connection.shutdown()
            call("sudo shutdown now", shell=True)
        if int(webdata[send_servo_data]) > 0:
            #dit versturen: id(3), voltage(42), movement speed(32), pres temperature(43), pres position(36), error shutdown(idk)(error 18)
            current_motor = motors[int(webdata[send_servo_data]) - 1]
            
            #TODO array maken waar alle info in komt
            data = []
            #get present position
            byte_seq = serial_connection.read_data(current_motor, 0x24, 2)
            position1 = utils.little_endian_bytes_to_int(byte_seq)
            position = utils.dxl_angle_to_degrees(position1)
            #get voltage
            byte_seq2 = serial_connection.read_data(current_motor, 0x2a, 1)
            raw_value = byte_seq2[0]
            voltage = raw_value / 10.
            #get movement speed
            byte_seq3 = serial_connection.read_data(current_motor, 0x20, 2)
            movementspd = utils.little_endian_bytes_to_int(byte_seq3)
            #get temperature
            byte_seq4 = serial_connection.read_data(current_motor, 0x2b, 2)
            temperature = utils.little_endian_bytes_to_int(byte_seq4)
            #get shutdown error message
            error = serial_connection.read_data(current_motor, 0x12, 2)
#            error = utils.little_endian_bytes_to_int(error)

            data.append(current_motor)
            data.append(raw_value)
            data.append(movementspd)
            data.append(temperature)
            data.append(position)
            data.append(error)
            #TODO Uitlezen van de 6 waarden
            conn.sendall(str(data).encode())
            
            
            


            
       
        

        if int(webdata[autonomous]) == 0:
            
            try:
                #print('check')
                #conn.sendall('flikker1'.encode())

                if  int(webdata[horizontal_rjoy]) > 2000:
                    #print('links')
                    serial_connection.goto(dynashoulder, 924, spda, degrees=False)
                elif int(webdata[horizontal_rjoy]) < 1600:
                    #print('rechts')
                    serial_connection.goto(dynashoulder, 100, spda, degrees=False)
                elif serial_connection.is_moving(dynashoulder):
                    cpos = serial_connection.get_present_position(dynashoulder, degrees=False)
                    
                    serial_connection.goto(dynashoulder, cpos, 1, degrees=False)

                if int(webdata[vertical_rjoy]) < 1600:
                    serial_connection.goto(dynaelbow, 100, spda, degrees=False)
                elif int(webdata[vertical_rjoy]) > 2000:
                    serial_connection.goto(dynaelbow, 924, spda, degrees=False)
                elif serial_connection.is_moving(dynaelbow):
                    cpos = serial_connection.get_present_position(dynaelbow, degrees=False)
                    serial_connection.goto(dynaelbow, cpos, 1, degrees=False)

                if int(webdata[vertical_ljoy]) > 2000:
                    serial_connection.goto(dynatrans, beneden, spdt, degrees=False)
                elif int(webdata[vertical_ljoy]) < 1600:
                    serial_connection.goto(dynatrans, boven, spdt, degrees=False)
                elif serial_connection.is_moving(dynatrans):
                    cpos = serial_connection.get_present_position(dynatrans, degrees=False)
                    serial_connection.goto(dynatrans, cpos, 1, degrees=False)

                if int(webdata[horizontal_ljoy]) > 2000:
                    serial_connection.goto(dynarot, 0, spdr, degrees=False)
                elif int(webdata[horizontal_ljoy]) < 1600:
                    serial_connection.goto(dynarot, 1023, spdr, degrees=False)
                elif serial_connection.is_moving(dynarot):
                    cpos = serial_connection.get_present_position(dynarot, degrees=False)
                    serial_connection.goto(dynarot, cpos, 1, degrees=False)

                if int(webdata[light]) == 1:
                    print('Ja')
                    serial_connection.goto(dynagrip, 823, spdg, degrees=False)
                elif int(webdata[light]) == 0:
                    print('Ja2')
                    serial_connection.goto(dynagrip, 200, spdg, degrees=False)

            except:
                continue
        else:
            print("Het systeem werkt autonoom!")
            #time.sleep(0.2)
            #TODO autonoom maken boem

            #TODO als bepaalde waardes veranderen dan moet er iets gebeuren

        #reactie = 'flikker'
        #conn.sendall(reactie.encode())
        #conn.sendall(txt)
    


#time.sleep(0.01)
#print("eind")



if __name__ == "__main__":
    test()


serial_connection.close()
#call('sudo shutdown now', shell=True)

