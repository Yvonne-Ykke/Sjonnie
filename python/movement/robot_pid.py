import time
from pyax12.connection import Connection
import time

SERVO_1 = 23
SERVO_2 = 3
SERVO_3 = 88

# Stel hier de PID-parameters in
Kp = 1.0
Ki = 0.1
Kd = 0.05

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        return output

class RobotArm:
    def __init__(self, connection):
        self.connection = connection
        self.shoulder_pid = PIDController(Kp, Ki, Kd)
        self.elbow_pid = PIDController(Kp, Ki, Kd)
        self.wrist_pid = PIDController(Kp, Ki, Kd)

    def move_to_position(self, shoulder_angle, elbow_angle, wrist_angle):
        if not self.connection:
            print("Serial connection not established.")
            return

        while True:
            current_shoulder_angle, current_elbow_angle, current_wrist_angle = self.get_angles_from_arm()

            # Bereken PID-uitvoer
            shoulder_output = self.shoulder_pid.compute(shoulder_angle, current_shoulder_angle)
            elbow_output = self.elbow_pid.compute(elbow_angle, current_elbow_angle)
            wrist_output = self.wrist_pid.compute(wrist_angle, current_wrist_angle)

            # Bepaal de snelheid op basis van de PID-uitvoer (beperk de snelheid tot een maximum waarde)
            shoulder_speed = min(max(abs(shoulder_output), 5), 50)  # Minimum snelheid 5, maximum snelheid 50
            elbow_speed = min(max(abs(elbow_output), 5), 50)
            wrist_speed = min(max(abs(wrist_output), 5), 50)

            # Beweeg servo's
            try:
                self.connection.goto(SERVO_1, current_shoulder_angle + shoulder_output, speed=shoulder_speed, degrees=True)
                time.sleep(0.1)
                self.connection.goto(SERVO_2, current_elbow_angle + elbow_output, speed=elbow_speed, degrees=True)
                time.sleep(0.1)
                self.connection.goto(SERVO_3, current_wrist_angle + wrist_output, speed=wrist_speed, degrees=True)
                time.sleep(0.1)

                print(f"Moving to position: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}, Wrist angle: {wrist_angle}")

                # Controleer of de huidige positie dicht genoeg bij de gewenste positie is
                if abs(shoulder_angle - current_shoulder_angle) < 0.5 and abs(elbow_angle - current_elbow_angle) < 0.5 and abs(wrist_angle - current_wrist_angle) < 0.5:
                    print("Position reached.")
                    break
            except Exception as e:
                print(f"Error moving to position: {e}")

    def get_angles_from_arm(self):
        if not self.connection:
            print("Serial connection not established.")
            return None, None, None
        try:
            shoulder_angle = self.connection.get_present_position(SERVO_1, degrees=True)
            elbow_angle = self.connection.get_present_position(SERVO_2, degrees=True)
            wrist_angle = self.connection.get_present_position(SERVO_3, degrees=True)
            return shoulder_angle, elbow_angle, wrist_angle
        except Exception as e:
            print(f"Error getting angles: {e}")
            return None, None, None

# Initialiseer de verbinding en de robotarm
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)
robot_arm = RobotArm(serial_connection)

# Voorbeeld van het verplaatsen naar een positie
robot_arm.move_to_position(0, 0, 45)