import subprocess
from pyax12.connection import Connection
from pyax12 import *
import time
import RPi.GPIO as GPIO
import signal
import sys
import socket
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#-- Constants --#              --------------------------------
BENEDEN = 1023
BOVEN = 0
SPEED_GRIPPER = 500
SPEED_ROTATION = 1.5
#-- Motor ID's --#             --------------------------------
SHOULDER = 61
ELBOW = 3
TRANS = 69
WRIST = 88
GRIPPER = 2
MOTORS = [ELBOW, SHOULDER, WRIST, TRANS, GRIPPER]
#-- Head type constants --#    --------------------------------
CYLINDER = 1
MARKER = 2
TOOLS = 3
#-- Web server constants --#   --------------------------------
SPEED_MODE = 0
TRANSLATION_SPEED_MODE = 1
POWER = 2
AUTONOMOUS = 3
LIGHT = 4
VERTICAL_RJOY = 5
HORIZONTAL_RJOY = 6
HORIZONTAL_LJOY = 7
VERTICAL_LJOY = 8
RASP_ON_OFF = 9
SEND_SERVO_DATA = 10
GRIP = 11
GRIPPER_HEAD_TYPE = 12

#-- Flag variables --#
flag = 0
butopenclose = 0

#-- Configuration --#
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer
# Open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Open serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True)
time.sleep(0.1)


#-- PC debug handling --#
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    s.shutdown(0)
    s.close()
    sys.exit(0)




#-- Send servo data --#
def read_and_send_servo_info(conn, webdata, spd, trns):

    data = []
    current_motor = MOTORS[webdata[SEND_SERVO_DATA] - 1]

    try:
        position_byte_sequence = serial_connection.read_data(current_motor, 0x24, 2)
        position = utils.little_endian_bytes_to_int(position_byte_sequence)
        position = utils.dxl_angle_to_degrees(position)

        if current_motor == SHOULDER | current_motor == ELBOW | current_motor == WRIST:
            spd = spd
        elif current_motor == TRANS:
            spd = trns
        elif current_motor == GRIPPER:
            spd = SPEED_GRIPPER
        motor_speed = spd

        voltage_byte_sequence = serial_connection.read_data(current_motor, 0x2a, 1)
        # voltage = voltage_byte_sequence[0]
        voltage = round(float(voltage_byte_sequence[0]*0.1), 2)

        temperature_byte_sequence = serial_connection.read_data(current_motor, 0x2b, 2)
        temperature = utils.little_endian_bytes_to_int(temperature_byte_sequence)

        error = "-"

        all_byte_sequences = [current_motor, voltage, motor_speed, temperature, position, error]
        for byte_sequence in all_byte_sequences:
            data.append(str(byte_sequence))

        result = ",".join(data)
        print(result)
        conn.send(result.encode())

    # Error handling
    except (Exception) as ex:
        exception_result = [str(current_motor),"-","-","-","-",str(ex)]
        result_to_string = ",".join(exception_result)
        conn.send(result_to_string.encode())




#-- Power off raspberry --#
def stop_rasp(conn):
    wait(1)
    conn.send('Raspberry uit'.encode())
    conn.close()
    subprocess.call("sudo shutdown now", shell=True)

#-- Readable wait function --#
def wait(wait_time_seconds):
    time.sleep(wait_time_seconds)

def whack_a_mole(webdata):
    #TODO: Whack a mole maken
    #TODO: Whack a mole maken
    SUPER_SPEED = 512
    WHACK_HIGH = 430
    WHACK_LOW = 345
    global flag
    global butopenclose

    if int(webdata[GRIP]) == 1:
        if butopenclose == 0:
            if flag == 1:
                serial_connection.goto(TRANS, WHACK_LOW, SUPER_SPEED, degrees=False)
                wait(0.1)
                serial_connection.goto(TRANS, WHACK_HIGH, SUPER_SPEED, degrees=False)
                flag = 0
            elif flag == 0:
                serial_connection.goto(TRANS, WHACK_LOW, SUPER_SPEED, degrees=False)
                wait(0.1)
                serial_connection.goto(TRANS, WHACK_HIGH, SUPER_SPEED, degrees=False)
                flag = 1
            butopenclose += 1
    if int(webdata[GRIP]) == 0:
        butopenclose = 0

def kilo_grip(conn, webdata):
    #TODO: Een stand maken waarij je weet dat je de kilo gripper hebt
    global butopenclose
    global flag

    if int(webdata[GRIP]) == 1:
        if butopenclose == 0:
            if flag == 1:
                serial_connection.goto(GRIPPER, 823, SPEED_GRIPPER, degrees=False)
                flag = 0
            elif flag == 0:
                serial_connection.goto(GRIPPER, 215, SPEED_GRIPPER, degrees=False)
                flag = 1
            butopenclose += 1
    if int(webdata[GRIP]) == 0:
        butopenclose = 0

def scissors_grip(webdata):
    #TODO: This
    global flag
    global butopenclose

    if int(webdata[GRIP]) == 1:
        if butopenclose == 0:
            if flag == 1:
                serial_connection.goto(GRIPPER, 583, SPEED_GRIPPER, degrees=False)
                flag = 0
            elif flag == 0:
                serial_connection.goto(GRIPPER, 350, SPEED_GRIPPER, degrees=False)
                flag = 1
            butopenclose += 1
    if int(webdata[GRIP]) == 0:
        butopenclose = 0
    print('tools grip')

def lights():
    #TODO: GPIO PIN HIGH AND OR LOW
    GPIO.setup(20,GPIO.OUT)
    GPIO.output(20,GPIO.HIGH)

    print('lights on off')

def pinch_grip(conn, webdata):
    #TODO: De gripper laten knijpen en krijgen welke gripper gebruikt wordt
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        whack_a_mole(webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == CYLINDER:
        kilo_grip(conn, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == TOOLS:
        scissors_grip(webdata)
    else:
        scissors_grip(webdata)

def handheld_control(conn, webdata, speed, trans_speed, pwr):
    #TODO: This
    try:
        pinch_grip(conn, webdata)
        #print('hhcontrol')

        pos = 0
        for value in webdata[VERTICAL_RJOY:VERTICAL_LJOY + 1]:
            if pos == 2:
                speed *= SPEED_ROTATION
            elif pos == 3:
                speed = trans_speed
            if value > 2000:
                max = 1023
                serial_connection.goto(MOTORS[pos], max, int(speed), degrees=False)
            elif value < 1600:
                min = 0
                serial_connection.goto(MOTORS[pos], min , int(speed), degrees=False)
            elif serial_connection.is_moving(MOTORS[pos]):
                current_motor_position = serial_connection.get_present_position(MOTORS[pos], degrees=False)
                serial_connection.goto(MOTORS[pos], current_motor_position, int(speed), degrees=False)
            pos += 1

    except (Exception) as ex:
        print("Handheld_Control_Error: " + str(ex))
        #conn.send("Handheld_Control_Error".encode())
        conn.close()


def autonomous_control(conn, webdata, speed, trans_speed, pwr, flag, butopenclose):
    #TODO: This
    try:
        pinch_grip(conn, webdata, flag, butopenclose)
    except:
        print("Autonomous_Control_Error")
        #conn.send("Autonomous_Control_Error".encode())
        conn.close()




def main():
    s.bind((HOST, PORT))
    wait(0.01)
    s.listen()
    wait(0.01)

    flag = 0
    butopenclose = 0
    while(True):
        #-- Getting data from webserver --#
        signal.signal(signal.SIGINT, signal_handler)
        conn, addr = s.accept()
        txt = conn.recv(1024)
        txt2 = txt.decode()
        # print(txt2)
        webdata = txt2.split(",")
        webdata = [int(value) for value in webdata]

        speed = int(webdata[SPEED_MODE])
        trans_speed = int(webdata[TRANSLATION_SPEED_MODE])
        pwr = int(webdata[POWER])

        #-- Functions --#
        if webdata[AUTONOMOUS] == 1:
            autonomous_control(conn, webdata, speed, trans_speed, pwr)
        else:
            handheld_control(conn, webdata, speed, trans_speed, pwr)

        if webdata[RASP_ON_OFF] == 1:
            stop_rasp(conn)

        if webdata[LIGHT] == 1:
            lights()

        if webdata[SEND_SERVO_DATA] > 0:
            read_and_send_servo_info(conn, webdata, speed, trans_speed)



if __name__ == "__main__":
    main()

serial_connection.close()


