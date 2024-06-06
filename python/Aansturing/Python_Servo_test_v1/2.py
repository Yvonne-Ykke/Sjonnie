import subprocess
from pyax12.connection import Connection
from pyax12 import *
import time
import RPi.GPIO as GPIO
import signal
import sys
#from subprocess import call

import socket

GPIO.setwarnings(False)

# Configuratie
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer
# Open webserver socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True)


beneden = 1023
boven = 0

#snelheid aanpassen op de servo
#spd = 25
#spdt = 100
#spda = 0.5
spdg = 500
spdr = 1.5

dynashoulder = 61
dynaelbow = 3
dynatrans = 69
dynarot = 88
dynagrip = 2

motors = [dynaelbow, dynashoulder, dynarot, dynatrans, dynagrip]

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
grip = 11





time.sleep(0.1)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    loop = False
    s.shutdown(0)
    s.close()
    print('doei')
    sys.exit(0)


def read_and_send_servo_info(conn, webdata, spd, trns):
    data = []
    current_motor = motors[webdata[send_servo_data] - 1]
    
    position = 0
    movementspd = 0
    temperature = 0
    raw_value = 0
    error = 0
    
    #get present position
    try:
        byte_seq = serial_connection.read_data(current_motor, 0x24, 2)
        position1 = utils.little_endian_bytes_to_int(byte_seq)
    
        position = utils.dxl_angle_to_degrees(position1)
        pos = 0
        if current_motor == dynashoulder | current_motor == dynaelbow | current_motor == dynarot:
            spd = spd
        elif current_motor == dynatrans:
            spd = trns
        elif current_motor == dynagrip:
            spd = spdg
        movementspd = spd

        #get voltage
        byte_seq2 = serial_connection.read_data(current_motor, 0x2a, 1)
        raw_value = byte_seq2[0]
        raw_value = round(float(raw_value*0.1), 2)
        #get movement speed
        #byte_seq3 = serial_connection.read_data(current_motor, 0x20, 2)
        #movementspd = utils.little_endian_bytes_to_int(byte_seq3)
        #get temperature
        byte_seq4 = serial_connection.read_data(current_motor, 0x2b, 2)
        temperature = utils.little_endian_bytes_to_int(byte_seq4)
        #get shutdown error message
    
        error = "-"

        sequences = [current_motor, raw_value, movementspd, temperature, position, error]
        for sequence in sequences:
             data.append(str(sequence))

        #re = str(data).replace(" ","").replace("[","").replace("]","")
        re = ",".join(data)
        print(re)

        #TODO Sturen van de 6 waarden
        conn.send(re.encode())

    except (Exception) as ex:
        print(ex)
        er = [str(current_motor),"-","-","-","-",str(ex)]
        err = ",".join(er)
        #print(err)
        #conn.send(err.encode())
        conn.send(err.encode())
        #error = serial_connection.read_data(current_motor, 0x12, 2)


    

def stop_rasp(conn):
    time.sleep(1)
    print('De raspberry sluit nu af. Doei!')
    conn.send('Raspberry uit'.encode())
    conn.close()
    #serial_connection.shutdown()
    subprocess.call("sudo shutdown now", shell=True)



def test():
    s.bind((HOST, PORT))
    time.sleep(0.01)
    s.listen()
    time.sleep(0.01)
    flag = 0
    ding = 0
    while(True):
        signal.signal(signal.SIGINT, signal_handler)
        #print(f'Server listening on {HOST}:{PORT}')
        conn, addr = s.accept()
        #print(f'Connected by {addr}')
        txt = conn.recv(1024)
        txt2 = txt.decode()
        print(txt2)
        webdata = txt2.split(",")
        webdata = [int(value) for value in webdata]  # Convert all values to integers
        #print(webdata[vertical_ljoy])
        spd = int(webdata[smode])
        trns = int(webdata[tranlation])
        pwr = int(webdata[power])
#        time.sleep(1)
        if int(webdata[rasp_onoff]) == 1:
            stop_rasp(conn)

        if int(webdata[send_servo_data]) > 0:
            #dit versturen: id(3), voltage(42), movement speed(32), pres temperature(43), pres position(36), error shutdown(idk)(error 18)
            read_and_send_servo_info(conn, webdata, spd, trns)


        if int(webdata[autonomous]) == 0:

            try:
                #print('check')
                #conn.sendall('flikker1'.encode())

                if int(webdata[grip]) == 1:
                    if ding == 0:
                        print('hello') #TODO verlichting toevoegen en daarvan pin aan en uit kunnen doen boem
                        if flag == 1:
                            serial_connection.goto(dynagrip, 823, spdg, degrees=False)
                            print('1ste')
                            flag = 0
                        elif flag == 0:
                            print('2de')
                            serial_connection.goto(dynagrip, 210, spdg, degrees=False)
                            flag = 1
                        ding += 1
                if int(webdata[grip]) == 0:
                    ding = 0



                pos = 0         
                for value in webdata[vertical_rjoy:vertical_ljoy + 1]:
                    #print(value)
                    if pos == 2: 
                        spd *= spdr
                    elif pos == 3:
                        spd = trns
                    
                    if value > 2000:
                        max = 1023
                        serial_connection.goto(motors[pos], max, int(spd), degrees=False)

                    elif value < 1600:
                        min = 0
                        serial_connection.goto(motors[pos], min , int(spd), degrees=False)

                    elif serial_connection.is_moving(motors[pos]):
                        cpos = serial_connection.get_present_position(motors[pos], degrees=False)
                        serial_connection.goto(motors[pos], cpos, int(spd), degrees=False)
                    #print(motors[pos])
                    pos += 1


                # if int(webdata[grip]) == 1:
                #     print('Ja')
                #     serial_connection.goto(dynagrip, 823, spdg, degrees=False)
                # elif int(webdata[grip]) == 0:
                #     print('Ja2')
                #     serial_connection.goto(dynagrip, 200, spdg, degrees=False)




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


