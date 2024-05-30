from pyax12.connection import Connection
import time
import moving

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3
# dynamixel_id3 = 10

def move_to_position(x,y):
    shoulder_angle, elbow_angle = moving.main(x,y)
    Connection.goto_position(servo_1, shoulder_angle, 100)
    Connection.goto_position(servo_2, elbow_angle, 100)