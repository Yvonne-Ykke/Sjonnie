from pyax12.connection import Connection
import RPi.GPIO as GPIO

SERVO_1 = 61
SERVO_2 = 3

class RobotArm:
    def __init__(self):
        try:
            self.serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)
            print("Serial connection established.")
        except Exception as e:
            print(f"Error establishing serial connection: {e}")
            self.serial_connection = None

        # GPIO pinnummer dat je wilt instellen
        pin_nummer = 18  # Bijvoorbeeld pin 18

        # GPIO initialisatie
        GPIO.setmode(GPIO.BCM)  # Gebruik BCM pinnummering

        # Zet de pin op uitvoer
        GPIO.setup(pin_nummer, GPIO.OUT)

    def move_to_position(self, shoulder_angle, elbow_angle):
        if not self.serial_connection:
            print("Serial connection not established.")
            return
        try:
            self.serial_connection.goto(SERVO_1, shoulder_angle, speed=20, degrees=True)
            self.serial_connection.goto(SERVO_2, elbow_angle, speed=20, degrees=True)
            print(f"Moving to position: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}")
        except Exception as e:
            print(f"Error moving to position: {e}")

    def get_angles_from_arm(self):
        if not self.serial_connection:
            print("Serial connection not established.")
            return None, None
        try:
            shoulder_angle = self.serial_connection.get_present_position(SERVO_1, degrees=True)
            elbow_angle = self.serial_connection.get_present_position(SERVO_2, degrees=True)
            return shoulder_angle, elbow_angle
        except Exception as e:
            print(f"Error getting angles: {e}")
            return None, None

    def close_connection(self):
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed.")
