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

beneden = 0
boven = 1023

spdt = 100
spda = 10
spdg = 300
dynatrans = 69
dynagrip = 2
dynashoulder = 61
dynaelbow = 3
dynarot = 88

time.sleep(0.1)

flag = 0

def send(dyn_id=None, position=None):
    #TODO Voeg hier een simpele read van de motor die positie opvangt
    cpos = serial_connection.get_present_position(dyn_id, degrees=False)
    
    spd = spda
    if dyn_id == dynagrip:
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
    if dyn_id == dynagrip:
        spd = spdg
    elif dyn_id == dynatrans:
        spd = spdt
    elif dyn_id == dynaelbow:
        spd = int(spda*2)
    elif dyn_id == dynarot:
        spd = int(spda*4)
    time.sleep(0.05)
    dist = abs(position-cpos)
    
    #if not serial_connection.is_moving(dyn_id):
    #    cpos = serial_connection.get_present_position(dyn_id, degrees=False)
            
    #TODO if distance is 20 dan ga die snelheid minderen
    if abs(position - cpos) > 350:
        #time.sleep(0.01)
        #serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.1), degrees=False)
        serial_connection.goto(dyn_id, position, speed=spd, degrees=False)
        #time.sleep(3)
        #serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.1), degrees=False)
    if abs(position - cpos) < 350:
#        serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.1), degrees=False)
        #time.sleep(5)
        serial_connection.goto(dyn_id, position, speed=spd, degrees=False)
        #serial_connection.goto(dyn_id, position, speed=int(abs(position-cpos)*0.01), degrees=False)


def stop():
    cpos1 = serial_connection.get_present_position(dynagrip, degrees=False)
    cpos2 = serial_connection.get_present_position(dynatrans, degrees=False)
    cpos3 = serial_connection.get_present_position(dynarot, degrees=False)
    cpos4 = serial_connection.get_present_position(dynaelbow, degrees=False)
    cpos5 = serial_connection.get_present_position(dynashoulder, degrees=False)
    try:
        serial_connection.goto(dynatrans, cpos2, 1, degrees=False)
        serial_connection.goto(dynagrip, cpos1, 1, degrees=False)
        serial_connection.goto(dynarot, cpos3, 1, degrees=False)
        serial_connection.goto(dynaelbow, cpos4, 1, degrees=False)
        serial_connection.goto(dynashoulder, cpos5, 1, degrees=False)
    except:
        print('oeps')

while True:
    
    c = stdscr.getch()
    if c == ord('w'): #vooruit
        smooth_send(dynaelbow, 512)
        #send(dyn2, 512)
    elif c == ord('a'): #links
        smooth_send(dynashoulder, 200)
        #send(dynamixel_id1, 200)
    elif c == ord('s'): #terug
        #TODO check of de positie van dyn1 helemaal links of rechts is ivm deadzone
        cpos = serial_connection.get_present_position(dynaelbow, degrees=False)
        if cpos < 512:
            smooth_send(dynaelbow, 50)
        elif cpos > 512:
            smooth_send(dynaelbow, 983)
        #send(dyn2, 200)
    elif c == ord('d'): #rechts
        smooth_send(dynashoulder, 900)
        #send(dynamixel_id1, 900)
    elif c == ord('k'): #translatie
        
        if flag == 0:
            print('naar beneden')
            send(dynatrans, 0)
            flag = 1  # Zet de vlag naar 1
        else:
            print('naar boven')
            send(dynatrans, 1023)
            flag = 0  # Zet de vlag naar 0
        #TODO naar boven wanneer weer erop klikken
        #TODO methode eraan toevoegen waardes zijn Motor, positie
    elif c == ord('g'): #translatie

        if flag == 0:
            print('open grip')
            send(dynagrip, 600)
            flag = 1  # Zet de vlag naar 1
        else:
            print('sluit grip')
            send(dynagrip, 200)
            
            flag = 0  # Zet de vlag naar 0
    elif c == ord('r'): #translatie
        
        if flag == 0:
            print('links')
            send(dynarot, 1023)
            flag = 1  # Zet de vlag naar 1
        else:
            print('rechts')
            send(dynarot, 0)
            flag = 0  # Zet de vlag naar 0
    elif c == ord('q'):
        break  # Exit the while loop
    elif c == curses.KEY_HOME:
        x = y = 0
    elif c == ord('z'):
        stop()


time.sleep(0.01)
print("eind")
# Close the serial connection
serial_connection.close()
s
