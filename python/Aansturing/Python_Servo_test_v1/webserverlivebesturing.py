from pyax12.connection import Connection
import time
import curses

stdscr = curses.initscr()

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

pos1 = 80 #als degrees false is dan is het van 0 tot 1023 en als het true is dan ist het van -150 tot 150
pos2 = 920
posm = 512

gopen = 300
gdicht = 30

beneden = 1023
boven = 0

spdt = 300
spda = 20
spdg = 500
dynatrans = 69
dynamixelgrip = 2
dynamixel_id1 = 10
dyn2 = 3

time.sleep(0.1)

flag = 0

def send(dyn_id=None, position=None):
    #TODO Voeg hier een simpele read van de motor die positie opvangt
    cpos = serial_connection.get_present_position(dyn_id, degrees=False)

    spd = spda
    if dyn_id == dynamixelgrip:
        spd = spdg
    elif dyn_id == dynatrans:
        spd = spdt
    time.sleep(0.05)
    dist = abs(position-cpos)
    if dist > cpos:
        dist+cpos
    elif dist < cpos:
        dist-cpos

    #time.sleep(0.1)
    serial_connection.goto(dyn_id, position, speed=spd, degrees=False)
    #time.sleep(3)
    #serial_connection.goto(dyn_id, position, speed=int(spd*0.1), degrees=False)
    #time.sleep(2)
    #serial_connection.goto(dyn_id, position, speed=int(spd*0.05), degrees=False)
    time.sleep(0.05)


def smooth_send(dyn_id, position):
    cpos = 0
    spd = spda
    if dyn_id == dynamixelgrip:
        spd = spdg
    elif dyn_id == dynatrans:
        spd = spdt
    time.sleep(0.05)
    dist = abs(position-cpos)

    if not serial_connection.is_moving(dyn_id):
        cpos = serial_connection.get_present_position(dyn_id, degrees=False)

    #TODO if distance is 20 dan ga die snelheid minderen
    if abs(position - cpos) > 350:
        time.sleep(0.01)
        serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.2), degrees=False)
        time.sleep(3)
        serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.1), degrees=False)
    if abs(position - cpos) < 350:
        serial_connection.goto(dyn_id, position, speed=int(abs(position-cpos)*0.1), degrees=False)
        time.sleep(5)
        serial_connection.goto(dyn_id, position, speed=int(abs(position-cpos)*0.01), degrees=False)






while True:

    c = stdscr.getch()
    if c == ord('w'): #vooruit
        smooth_send(dyn2, 512)
        #send(dyn2, 512)
    elif c == ord('a'): #links
        smooth_send(dynamixel_id1, 200)
        #send(dynamixel_id1, 200)
    elif c == ord('s'): #terug
        #TODO check of de positie van dyn1 helemaal links of rechts is ivm deadzone
        smooth_send(dyn2, 200)
        #send(dyn2, 200)
    elif c == ord('d'): #rechts
        smooth_send(dynamixel_id1, 900)
        #send(dynamixel_id1, 900)
    elif c == ord('k'): #translatie

        if flag == 0:
            print('naar beneden')
            send(dynatrans, 1023)
            flag = 1  # Zet de vlag naar 1
        else:
            print('naar boven')
            send(dynatrans, 0)
            flag = 0  # Zet de vlag naar 0
        #TODO naar boven wanneer weer erop klikken
        #TODO methode eraan toevoegen waardes zijn Motor, positie
    elif c == ord('q'):
        break  # Exit the while loop
    elif c == curses.KEY_HOME:
        x = y = 0


time.sleep(0.01)
print("eind")
# Close the serial connection
serial_connection.close()




import socket
import time
# Configuratie
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

time.sleep(0.01)
def test():

    s.bind((HOST, PORT))
    time.sleep(0.01)
    s.listen()
    time.sleep(0.01)

    while(True):
        #print(f'Server listening on {HOST}:{PORT}')
        conn, addr = s.accept()
        #print(f'Connected by {addr}')

        data = conn.recv(1024)
        if data:
            print(f'Recieved: {data.decode()}')

        #conn.sendall(reactie.encode())
        conn.sendall(data)
    #TODO een ifstatement die leest of er gevraagd word om de servo uit te lezen
    #TODO de servo uilezen
    #TODO de inhoud doorsturen

if __name__ == "__main__":
    test()

s.shutdown()
s.close()




