import socket
from pyax12.connection import Connection
import sys
import signal

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3

def move_to_position(shoulder_angle, elbow_angle):
    serial_connection.goto(servo_1, 0, speed = 100, degrees = True)
    serial_connection.goto(servo_2, 0, speed = 100, degrees = True)
    print(f"Bewegen naar positie: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")
