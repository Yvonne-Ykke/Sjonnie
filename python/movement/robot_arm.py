from pyax12.connection import Connection
import pyax12 
import time

SERVO_1 = 23
SERVO_2 = 3
SERVO_3 = 88

#serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

class RobotArm:
    def move_to_position(shoulder_angle, elbow_angle, wrist_angle, serial_connection):
            if not serial_connection:
                print("Serial connection not established.")
                return
            try:
                print("serial_connection: ", serial_connection)
                serial_connection.goto(SERVO_1, int(shoulder_angle), speed=20, degrees=True)
                print("1")
                time.sleep(0.1)  # Korte vertraging toevoegen
                serial_connection.goto(SERVO_2, int(elbow_angle), speed=20, degrees=True)
                print("2")
                time.sleep(0.1)  # Korte vertraging toevoegen
                serial_connection.goto(SERVO_3, int(wrist_angle), speed=20, degrees=True)
                print("3")
                time.sleep(0.1)  # Korte vertraging toevoegen
    
                print(f"Moving to position: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}, Wrist angle: {wrist_angle}")
            except Exception as e:
                print(f"Error moving to position: {e}")

    def get_angles_from_arm():
        if not serial_connection:
            print("Serial connection not established.")
            return None, None
        try:
            shoulder_angle = serial_connection.get_present_position(SERVO_1, degrees=True)
            elbow_angle = serial_connection.get_present_position(SERVO_2, degrees=True)
            wrist_angle = serial_connection.get_present_position(SERVO_3, degrees=True)
            return shoulder_angle, elbow_angle, wrist_angle
        except Exception as e:
            print(f"Error getting angles: {e}")
            return None, None

    def close_connection():
        if serial_connection:
            serial_connection.close()
            print("Serial connection closed.")
