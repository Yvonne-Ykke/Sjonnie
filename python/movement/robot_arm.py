import angle_calculator
from pyax12.connection import Connection

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

SERVO_1 = 61
SERVO_2 = 3

def move_to_position(shoulder_angle, elbow_angle):
    serial_connection.goto(SERVO_1, shoulder_angle, speed = 20, degrees = True)
    serial_connection.goto(SERVO_2, elbow_angle, speed = 20, degrees = True)
    print(f"Bewegen naar positie: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")
    serial_connection.close()

def get_angles_from_arm():
    shoulder_angle = serial_connection.get_present_position(SERVO_1, degrees=True)
    elbow_angle = serial_connection.get_present_position(SERVO_2, degrees=True)
    return shoulder_angle, elbow_angle

def main():
    new_x, new_y = 100, 100
    angle_calculator.main(new_x, new_y, get_angles_from_arm())
    pass