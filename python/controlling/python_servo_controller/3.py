import subprocess
from pyax12.connection import Connection
from pyax12 import *
import time
import RPi.GPIO as GPIO
import signal
import sys
import socket
GPIO.setwarnings(False)

#-- Constants --#
beneden = 1023
boven = 0
speed_gripper = 500
speed_rotation = 1.5
flag = 0
ding = 0

#-- Motor ID's --#
shoulder = 61
elbow = 3
trans = 69
wrist = 88
gripper = 2
motors = [elbow, shoulder, wrist, trans, gripper] 

#-- Web server constants --#
speed_mode = 0
translation_speed_mode = 1
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


#-- Configuration --#
HOST = '0.0.0.0'  # Luister op alle beschikbare interfaces
PORT = 65432      # Kies een poortnummer
# Open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#-- Open serial port --#
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
    #-- Define Variables --#
    # position = 0
    # movementspeed = 0
    # temperature = 0
    # voltage = 0
    # error = 0
    data = []
    current_motor = motors[webdata[send_servo_data] - 1]

    try:
        position_byte_sequence = serial_connection.read_data(current_motor, 0x24, 2)
        position = utils.little_endian_bytes_to_int(position_byte_sequence)
        position = utils.dxl_angle_to_degrees(position)

        if current_motor == shoulder | current_motor == elbow | current_motor == wrist:
            spd = spd
        elif current_motor == trans:
            spd = trns
        elif current_motor == gripper:
            spd = speed_gripper
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
    time.sleep(1)
    conn.send('Raspberry uit'.encode())
    conn.close()
    subprocess.call("sudo shutdown now", shell=True)

#-- Readable wait function --#
def wait(wait_time_seconds):
    time.sleep(wait_time_seconds)

def whack_a_mole(conn):
    #TODO: Whack a mole maken
    1+1

def kilo_grip(conn, webdata):
    #TODO: Een stand maken waarij je weet dat je de kilo gripper hebt
    1+1

def scissors_grip(conn, webdata):
    #TODO: This
    1+1

def lights(conn, webdata):
    1+1


def handheld_control(conn, webdata, speed, trans_speed, pwr, flag, ding):
    #TODO: This

    #-- Define additional variables --#

    try:

        pos = 0
        for value in webdata[vertical_rjoy:vertical_ljoy + 1]:
            if pos == 2:
                speed *= speed_rotation
            elif pos == 3:
                speed = trans_speed
            if value > 2000:
                max = 1023
                serial_connection.goto(motors[pos], max, int(speed), degrees=False)
            elif value < 1600:
                min = 0
                serial_connection.goto(motors[pos], min , int(speed), degrees=False)
            elif serial_connection.is_moving(motors[pos]):
                current_motor_position = serial_connection.get_present_position(motors[pos], degrees=False)
                serial_connection.goto(motors[pos], current_motor_position, int(speed), degrees=False)
            pos += 1

    except Exception as ex:
        print("Error")
        #conn.send("Error".encode())
        conn.close()




def main():
    s.bind((HOST, PORT))
    wait(0.01)
    s.listen()
    wait(0.01)
    flag = 0
    ding = 0
    while(True):
        #-- Getting data from webserver --#
        signal.signal(signal.SIGINT, signal_handler)
        conn, addr = s.accept()
        txt = conn.recv(1024)
        txt2 = txt.decode()
        print(txt2)
        webdata = txt2.split(",")
        webdata = [int(value) for value in webdata]

        speed = int(webdata[speed_mode])
        trans_speed = int(webdata[translation_speed_mode])
        pwr = int(webdata[power])

        #-- Functions --#
        if webdata[rasp_onoff] == 1:
            stop_rasp(conn)

        if webdata[light] == 1:
            lights()

        if webdata[send_servo_data] > 0:
            read_and_send_servo_info(conn, webdata, speed, trans_speed)

        if webdata[autonomous] != 0:
            #TODO: autonoom maken/ script aanroepen die dat voor je doet
            #TODO: als bepaalde waardes veranderen dan moet er iets gebeuren
            if webdata[autonomous] == 1:
                whack_a_mole(conn)
            elif webdata[autonomous] == 2:
                kilo_grip(conn, webdata)
            elif webdata[autonomous] == 3:
                scissors_grip(conn, webdata)

        else:
            handheld_control(conn, webdata, speed, trans_speed, pwr, flag, ding)


if __name__ == "__main__":
    main()

serial_connection.close()
