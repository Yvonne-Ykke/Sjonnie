from pyax12.connection import Connection
import time
import curses

import socket
import time

stdscr = curses.initscr()

# Configuratie
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer
# Open webserver socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

pos1 = 80 #als degrees false is dan is het van 0 tot 1023 en als het true is dan ist het van -150 tot 150
pos2 = 920
posm = 512

gopen = 300
gclosed = 30

beneden = 1023
boven = 0

spdt = 100
spda = 25
spdg = 500

dynatrans = 69
dynagrip = 2
dynashoulder = 10
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

time.sleep(0.1)

def test():

    s.bind((HOST, PORT))
    time.sleep(0.01)
    s.listen()
    time.sleep(0.01)

    while(True):
        #print(f'Server listening on {HOST}:{PORT}')
        conn, addr = s.accept()
        #print(f'Connected by {addr}')

        txt = conn.recv(1024)
        txt2 = txt.decode()
        #print(txt2)
        webdata = txt2.split(",")
        #print(webdata[vertical_ljoy])

        if webdata[light] == 1:
            #TODO verlichting aan boem
            light1 = 1
        else:
            #TODO verlichting uit boem
            light1 = 0

        if int(webdata[autonomous]) == 0:
            try:
                if  int(webdata[horizontal_rjoy]) > 2000:
                    #print('rechts schouder')
                    serial_connection.goto(dynashoulder, 924, spda, degrees=False)
                elif int(webdata[horizontal_rjoy]) < 1600:
                    #print('links schouder')
                    serial_connection.goto(dynashoulder, 100, spda, degrees=False)
                elif serial_connection.is_moving(dynashoulder):
                    cpos = serial_connection.get_present_position(dynashoulder, degrees=False)
                    #print('rem schouder')
                    serial_connection.goto(dynashoulder, cpos, 1, degrees=False)
                #time.sleep(0.01)

                if int(webdata[vertical_rjoy]) > 2000:
                    #ga naar voren (incl berekening hoek)
                    #print('links elleboog')
                    serial_connection.goto(dynaelbow, 100, spda, degrees=False)
                elif int(webdata[vertical_rjoy]) < 1600:
                    #ga naar achteren (zie voren)
                    #print('rechts elleboog')
                    serial_connection.goto(dynaelbow, 924, spda, degrees=False)
                elif serial_connection.is_moving(dynaelbow):
                    cpos = serial_connection.get_present_position(dynaelbow, degrees=False)
                    #print('rem elleboog')
                    serial_connection.goto(dynaelbow, cpos, 1, degrees=False)
                #time.sleep(0.01)

                if int(webdata[vertical_ljoy]) > 2000:
                    #print('omhoog')
                    serial_connection.goto(dynatrans, boven, spdt, degrees=False)
                elif int(webdata[vertical_ljoy]) < 1600:
                    #print('omlaag')
                    serial_connection.goto(dynatrans, beneden, spdt, degrees=False)
                elif serial_connection.is_moving(dynatrans):
                    cpos = serial_connection.get_present_position(dynatrans, degrees=False)
                    #print('rem verticaal')
                    serial_connection.goto(dynatrans, cpos, 1, degrees=False)
                #time.sleep(0.01)

            except:
                continue



        else:
            print("Het systeem werkt autonoom!")
            #time.sleep(0.2)
            #TODO autonoom maken boem

            #TODO als bepaalde waardes veranderen dan moet er iets gebeuren


        #conn.sendall(reactie.encode())
        conn.sendall(txt)


time.sleep(0.01)
print("eind")


if __name__ == "__main__":
    test()

serial_connection.close()


