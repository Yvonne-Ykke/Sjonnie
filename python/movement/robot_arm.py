from pyax12.connection import Connection
import RPi.GPIO as GPIO
import time

SERVO_1 = 23
SERVO_2 = 3

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)
GPIO.setup(18, GPIO.OUT)

class RobotArm:
    def move_to_position(self, shoulder_angle, elbow_angle):
            if not serial_connection:
                print("Serial connection not established.")
                return
            try:
                serial_connection.goto(SERVO_1, shoulder_angle, speed=20, degrees=True)
                time.sleep(0.1)  # Korte vertraging toevoegen
                serial_connection.goto(SERVO_2, elbow_angle, speed=20, degrees=True)
                time.sleep(0.1)  # Korte vertraging toevoegen
                print(serial_connection.ping(SERVO_1))
                print(serial_connection.ping(SERVO_2))
                print(f"Moving to position: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}")
            except Exception as e:
                print(f"Error moving to position: {e}")

    def get_angles_from_arm(self):
        if not serial_connection:
            print("Serial connection not established.")
            return None, None
        try:
            shoulder_angle = serial_connection.get_present_position(SERVO_1, degrees=True)
            elbow_angle = serial_connection.get_present_position(SERVO_2, degrees=True)
            return shoulder_angle, elbow_angle
        except Exception as e:
            print(f"Error getting angles: {e}")
            return None, None

    def close_connection(self):
        if serial_connection:
            serial_connection.close()
            print("Serial connection closed.")
