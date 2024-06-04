from pyax12.connection import Connection
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
pos1 = 80 #als degrees false is dan is het van 0 tot 1023 en als het true is dan ist het van -150 tot 150
pos2 = 920
posm = 512

gopen = 300
gclosed = 30

beneden = 980
boven = 0

spdt = 100
spda = 25
spdg = 500
spdr = 100

dynatrans = 69
dynagrip = 2
dynarot = 88 
dynashoulder = 61
dynaelbow = 3

smode = 0
tranlation = 1
power = 2
autonomous = 3
light = 4
horizontal_ljoy = 5
vertical_ljoy = 6
vertical_rjoy = 7
horizontal_rjoy = 8
rasp_onoff = 9


time.sleep(0.1)

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
        #if int(webdata[rasp_onoff]) == 1:
        #    time.sleep(1)
        #    print('De raspberry sluit nu af. Doei!')
        #    conn.send('Raspberry uit')
        #    conn.close()
        #    serial_connection.shutdown()
        #    call("sudo shutdown now", shell=True)

       
        

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

                if int(webdata[vertical_rjoy]) > 2000:
                    serial_connection.goto(dynaelbow, 100, spda, degrees=False)
                elif int(webdata[vertical_rjoy]) < 1600:
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

                #if int(webdata[horizontal_ljoy]) > 2000:
                #    serial_connection.goto(dynarot, 0, spdr, degrees=False)
                #elif int(webdata[horizontal_ljoy]) < 1600:
                #    serial_connection.goto(dynarot, 1023, spdr, degrees=False)
                #elif serial_connection.is_moving(dynarot):
                #    cpos = serial_connection.get_present_position(dynarot, degrees=False)
                #    serial_connection.goto(dynarot, cpos, 1, degrees=False)

                if int(webdata[light]) == 1:
                    print('Ja')
                    serial_connection.goto(dynagrip, 1023, spdg, degrees=False)
                elif int(webdata[light]) == 0:
                    print('Ja2')
                    serial_connection.goto(dynagrip, 0, spdg, degrees=False)




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

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    serial_connection.close()
    s.shutdown(0)
    s.close()
    sys.exit(0)


if __name__ == "__main__":
    test()


serial_connection.close()
#call('sudo shutdown now', shell=True)

