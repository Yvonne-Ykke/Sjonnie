import subprocess
from pyax12.connection import Connection
from pyax12 import *
import pyax12.packet as pk
import time
import RPi.GPIO as GPIO
import signal
import sys
import socket
import cv2 as cv
import threading
import controls
import struct
#import fcntl

sys.path.append('/home/sjonnie/git/Sjonnie/python/computer_vision')
import contour

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


#-- Constants --#              --------------------------------
BENEDEN = 1023
BOVEN = 0
SPEED_GRIPPER = 500
SPEED_ROTATION = 1.5
#-- Motor ID's --#             --------------------------------
SHOULDER = 23
ELBOW = 3
TRANS = 11
WRIST = 88
GRIPPER = 2
MOTORS = [ELBOW, SHOULDER, WRIST, TRANS, GRIPPER]
PEN_MOTORS = [ELBOW, SHOULDER, TRANS]
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
COLOR = 13

#-- Configuration --#
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer

# Open socket
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
##TODO copy current motor and make is penmotors

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

def get_data():
    conn, addr = s.accept()
    txt = conn.recv(2048)
    txt2 = txt.decode()
    print(txt2)
    webdata = txt2.split(",")
    return webdata, conn

def start_socket():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    wait(0.01)
    s.listen()
    wait(0.01)

def main():
    start_socket()
    wait(0.01)
    cap = cv.VideoCapture(0)
    wait(0.01)
    serial_connection.write_data(88, pk.CW_COMPLIENCE_SLOPE, 3)
    serial_connection.write_data(88, pk.CCW_COMPLIENCE_SLOPE, 3)
    conn, addr = s.accept()
    conn.recv(1024)
    flag = 0
    butopenclose = 0
    while(True):
        #-- Getting data from webserver --#
        signal.signal(signal.SIGINT, signal_handler)
        webdata, conn = get_data()

        if len(webdata) > 2:
            webdata = [int(value) for value in webdata]

            speed = int(webdata[SPEED_MODE])
            trans_speed = int(webdata[TRANSLATION_SPEED_MODE])
            pwr = int(webdata[POWER])

#            ret,img = cap.read()

        #-- Functions --#
            if webdata[AUTONOMOUS] == 1:
                ret,img = cap.read()
                time.sleep(0.01)
                controls.autonomous_control(serial_connection, conn, webdata, speed, trans_speed, pwr, img)
                start_socket()
            else:
                controls.handheld_control(serial_connection, conn, webdata, speed, trans_speed, pwr)

            if webdata[RASP_ON_OFF] == 1:
                stop_rasp(conn)

            if webdata[SEND_SERVO_DATA] > 0:
                read_and_send_servo_info(conn, webdata, speed, trans_speed)

            if webdata[POWER] == 150:
                print('"Gripper Force = Power" terwijl er geen force modus is dus programma sluit af.')
                raise('Programma sluit af')


if __name__ == "__main__":
    main()

serial_connection.close()


