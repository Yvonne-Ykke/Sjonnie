import subprocess
from pyax12.connection import Connection
from pyax12 import *
import time
#import RPi.GPIO as GPIO
import signal
import sys
import socket
import cv2 as cv
import threading

sys.path.append('/home/sjonnie/git/Sjonnie/python/computer_vision')
import contour
import main

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
AUTO_MODE = 4
VERTICAL_RJOY = 5
HORIZONTAL_RJOY = 6
HORIZONTAL_LJOY = 7
VERTICAL_LJOY = 8
RASP_ON_OFF = 9
SEND_SERVO_DATA = 10
GRIP = 11
GRIPPER_HEAD_TYPE = 12
COLOR = 13

#-- Flag variables --#
flag = 0
butopenclose = 0

def whack_a_mole(serial_connection, webdata):
    WHACK_SPEED = 512
    WHACK_HIGH = 110
    WHACK_LOW = 0
    global flag
    global butopenclose
    if int(webdata[GRIP]) == 1:
        if butopenclose == 0:
            if flag == 1:
                serial_connection.goto(TRANS, WHACK_LOW, WHACK_SPEED, degrees=False)
                wait(0.1)
                serial_connection.goto(TRANS, WHACK_HIGH, WHACK_SPEED, degrees=False)
                flag = 0
            elif flag == 0:
                serial_connection.goto(TRANS, WHACK_LOW, WHACK_SPEED, degrees=False)
                wait(0.1)
                serial_connection.goto(TRANS, WHACK_HIGH, WHACK_SPEED, degrees=False)
                flag = 1
            butopenclose += 1
    if int(webdata[GRIP]) == 0:
        butopenclose = 0

def auto_grab(open_or_closed, serial_connection, spd=None):
    HIGH = 1023
    LOW = 100
    OPEN = 600
    CLOSED = 350
    pos = CLOSED
    if open_or_closed == 'open':
        pos = OPEN    
    serial_connection.goto(TRANS, LOW, spd, degrees=False)
    if serial_connection.is_moving(TRANS):
        print('Moving to low position')
        auto_grab(open_or_closed, serial_connection, spd)
    else:
        serial_connection.goto(GRIPPER, pos, spd, degrees=False)
        time.sleep(0.2)
        serial_connection.goto(TRANS, HIGH, spd, degrees=False)


def kilo_grip(serial_connection, conn, webdata):
    global butopenclose
    global flag
    if int(webdata[GRIP]) == 1:
        if butopenclose == 0:
            if flag == 1:
                serial_connection.goto(GRIPPER, 823, SPEED_GRIPPER, degrees=False)
                flag = 0
            elif flag == 0:
                serial_connection.goto(GRIPPER, 250, SPEED_GRIPPER, degrees=False)
                flag = 1
            butopenclose += 1
    if int(webdata[GRIP]) == 0:
        butopenclose = 0

def scissors_grip(serial_connection, webdata):
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

def pinch_grip(serial_connection, conn, webdata):
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        whack_a_mole(serial_connection, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == CYLINDER:
        kilo_grip(serial_connection, conn, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == TOOLS:
        scissors_grip(serial_connection, webdata)

def all_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr):
    pos = 0
    try:
        pinch_grip(serial_connection, conn, webdata)
        for value in webdata[VERTICAL_RJOY:VERTICAL_LJOY + 1]:
            if pos == 2:
                speed *= SPEED_ROTATION
            elif pos == 3:
                speed = trans_speed
            if value > 2000:
                max = 1020
                serial_connection.goto(MOTORS[pos], max, int(speed), degrees=False)
                print('rechts')
            elif value < 1600:
                min = 3
                serial_connection.goto(MOTORS[pos], min, int(speed), degrees=False)
                print('links')
            elif serial_connection.is_moving(MOTORS[pos]):
                current_motor_position = serial_connection.get_present_position(MOTORS[pos], degrees=False)
                serial_connection.goto(MOTORS[pos], current_motor_position, int(speed), degrees=False)
            pos += 1

    except (Exception) as ex:
        if ex == TypeError:
            print("Motor: " + str(MOTORS[pos]) + " not connected.")
            print("Suggestion: Selcect different gripperhead in: Settings - Gripper.")
        else:
            print("A_M_Controls.Handheld_Control_Error: " + str(ex) + " Motor: " + str(MOTORS[pos]))
        conn.close()

def pen_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr):
    pos = 0
    try:
        pinch_grip(serial_connection, conn, webdata)
        for value in webdata[VERTICAL_RJOY:HORIZONTAL_RJOY + 1]:
            if value > 2000:
                max = 1020
                serial_connection.goto(PEN_MOTORS[pos], max, int(speed), degrees=False)
            elif value < 1600:
                min = 3
                serial_connection.goto(PEN_MOTORS[pos], min, int(speed), degrees=False)
            elif serial_connection.is_moving(PEN_MOTORS[pos]):
                current_motor_position = serial_connection.get_present_position(PEN_MOTORS[pos], degrees=False)
                serial_connection.goto(PEN_MOTORS[pos], current_motor_position, int(speed), degrees=False)
            pos += 1

    except (Exception) as ex:
        print("PEN_M_Controls.Handheld_Control_Error: " + str(ex) + " Motor: " + str(PEN_MOTORS[pos]))
        conn.close()

def autonomous_control(serial_connection, conn, webdata, speed, trans_speed, pwr, img):
    if img is not None:

        color_mode = webdata[COLOR]
        contour_mode = webdata[GRIPPER_HEAD_TYPE]
        #TODO = alleen contouring gebruiken ipv color wnr kan
        if webdata[AUTO_MODE]:
            #Dynamic mode
            print('Dynamic mode')
            if webdata[GRIPPER_HEAD_TYPE] == MARKER:
                #TODO: een autonoom script aanroepen en wanneer er een stip moet komen de whack a mole functie aanroepen.
                whack_a_mole(serial_connection, webdata)
            elif webdata[GRIPPER_HEAD_TYPE] == CYLINDER:
                print('Autonomous error: Wrong gripper selected. Reccomended: "Pen" or "Tools"')
            elif webdata[GRIPPER_HEAD_TYPE] == TOOLS:
                #TODO: in contouring het goed opvangen (standen: statisch contour, dynamisch contour of individuele kleur, whackamole)
                contour.color_contouring(serial_connection, False, 'scissors', color_mode, img, True)
                #TODO: daadwerkelijk bewegen
                #contour.contour_main(False, 'scissors', color_mode, img)
                #TODO: wanneer knijpen moet, roep pinch grip of scissors
        else:
            #Static mode
            print('Static mode')
            color_mode = 0
            contour.color_contouring(serial_connection, False, 'scissors', color_mode, img, False)
    else:
        print('Autonomous_mode error: Image is none')
        raise('Image_None Error')

def handheld_control(serial_connection, conn, webdata, speed, trans_speed, pwr):
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        pen_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr)
    else:
        all_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr)




