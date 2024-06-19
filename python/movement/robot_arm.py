from pyax12.connection import Connection
import time

SHOULDER_SERVO = 23
ELBOW_SERVO = 3
WRIST_SERVO = 88
GRIPPER_SERVO = 2
GRIPPER_HEIGHT_SERVO = 11

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

class RobotArm:
    @staticmethod
    def move_to_position(shoulder_angle, elbow_angle, wrist_angle):
        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(SHOULDER_SERVO, shoulder_angle, speed=20, degrees=True)
            time.sleep(0.1)  # Korte vertraging toevoegen
            serial_connection.goto(ELBOW_SERVO, elbow_angle, speed=20, degrees=True)
            time.sleep(0.1)  # Korte vertraging toevoegen
            serial_connection.goto(WRIST_SERVO, wrist_angle, speed=20, degrees=True)
            time.sleep(0.1)  # Korte vertraging toevoegen
    
            print(f"Moving to position: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}, Wrist angle: {wrist_angle}")
        except Exception as e:
            print(f"Error moving to position: {e}")

    @staticmethod
    def get_angles_from_arm():
        if not serial_connection:
            print("Serial connection not established.")
            return None, None, None
        try:
            shoulder_angle = serial_connection.get_present_position(SHOULDER_SERVO, degrees=True)
            elbow_angle = serial_connection.get_present_position(ELBOW_SERVO, degrees=True)
            wrist_angle = serial_connection.get_present_position(WRIST_SERVO, degrees=True)
            return shoulder_angle, elbow_angle, wrist_angle
        except Exception as e:
            print(f"Error getting angles: {e}")
            return None, None, None

    @staticmethod
    def gripper_open():
        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(GRIPPER_SERVO, 583, speed=50)  # Open gripper
            print("Gripper opened.")
        except Exception as e:
            print(f"Error opening gripper: {e}")

    @staticmethod
    def gripper_close():
        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(GRIPPER_SERVO, 350, speed=50)  # Close gripper
            print("Gripper closed.")
        except Exception as e:
            print(f"Error closing gripper: {e}")

    @staticmethod
    def gripper_up():
        GRIPPER_MAX_HEIGHT = 1023
        TRANSLATION_SPEED = 50
        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(GRIPPER_HEIGHT_SERVO, GRIPPER_MAX_HEIGHT, speed=TRANSLATION_SPEED)  # Move gripper up
            print("Gripper moved up.")
        except Exception as e:
            print(f"Error moving gripper up: {e}")

    @staticmethod
    def gripper_down():
        GRIPPER_MIN_HEIGHT = 3
        TRANSLATION_SPEED = 50

        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(GRIPPER_HEIGHT_SERVO, GRIPPER_MIN_HEIGHT, speed=TRANSLATION_SPEED)  # Move gripper down
            print("Gripper moved down.")
        except Exception as e:
            print(f"Error moving gripper down: {e}")

    @staticmethod
    def wrist_rotate(angle):
        TRANSLATION_SPEED = 50
        if not serial_connection:
            print("Serial connection not established.")
            return
        try:
            serial_connection.goto(WRIST_SERVO, angle, speed=TRANSLATION_SPEED, degrees=True)
            print(f"Wrist rotated to angle: {angle} degrees.")
        except Exception as e:
            print(f"Error rotating wrist: {e}")

    @staticmethod
    def close_connection():
        if serial_connection:
            serial_connection.close()
            print("Serial connection closed.")
