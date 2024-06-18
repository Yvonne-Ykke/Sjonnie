import subprocess
from pyax12.connection import Connection
from pyax12 import *
import time
import RPi.GPIO as GPIO
import signal
import sys
import socket
import cv2 as cv
import threading

sys.path.append('../../computer_vision/')
import contour

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

#-- Flag variables --#
flag = 0
butopenclose = 0

def whack_a_mole(serial_connection, webdata):
    #TODO: Whack a mole maken
    #TODO: Whack a mole maken
    SUPER_SPEED = 512
    WHACK_HIGH = 110
    WHACK_LOW = 0
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

def kilo_grip(serial_connection, conn, webdata):
    #TODO: Een stand maken waarij je weet dat je de kilo gripper hebt
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
    

def lights():
    #TODO: GPIO PIN HIGH AND OR LOW
    GPIO.setup(20,GPIO.OUT)
    GPIO.output(20,GPIO.HIGH)

    print('lights on off')


def pinch_grip(serial_connection, conn, webdata):
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        whack_a_mole(webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == CYLINDER:
        kilo_grip(serial_connection, conn, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == TOOLS:
        scissors_grip(webdata)
    else:
        scissors_grip(webdata)


def handheld_control(serial_connection, conn, webdata, speed, trans_speed, pwr):
    #TODO: Check of het standje pen is of niet(zo wel dan zijn er maar 3 motors en anders 5)
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        pen_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr)
    else:
        all_motors_control(serial_connection, conn, webdata, speed, trans_speed, pwr)


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
            print("Controls.Handheld_Control_Error: " + str(ex) + " Motor: " + str(MOTORS[pos]))
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
        print("Handheld_Control_Error: " + str(ex) + " Motor: " + str(PEN_MOTORS[pos]))
        #conn.send("Handheld_Control_Error".encode())
        conn.close()


def autonomous_control(serial_connection, conn, webdata, speed, trans_speed, pwr, img):
    #TODO: This

    color_mode = webdata[COLOR]
    contour_mode = webdata[GRIPPER_HEAD_TYPE]
    if webdata[GRIPPER_HEAD_TYPE] == MARKER:
        #TODO: whack a mole autonoom maken
        whack_a_mole(serial_connection, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == CYLINDER:
        #TODO: kilo grip autonoom maken
        kilo_grip(serial_connection, conn, webdata)
    elif webdata[GRIPPER_HEAD_TYPE] == TOOLS:
        contour.color_contouring(False, 'scissors', color_mode, img)

    try:
        contour.color_contouring(False, contour_mode, color_mode, img)
    except (Exception) as ex:
        print("Autonomous_Control_Error: " + str(ex))
        #conn.send("Autonomous_Control_Error".encode())
        conn.close()
