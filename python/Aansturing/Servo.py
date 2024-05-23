from gpiozero import Servo
from time import sleep
import math

class ServoMotor:
    def __init__(self, gpio_pin):
        self.servo = Servo(gpio_pin)
        self.angle = 0
    
    def move_to_angle(self, angle):
        self.angle = angle
        self.servo.value = angle / 90 - 1  # Convert 0-180 degrees to -1 to 1 range

class SCARARobotArm:
    def __init__(self, servo_pin_1, servo_pin_2, link1_length, link2_length):
        self.servo1 = ServoMotor(servo_pin_1)
        self.servo2 = ServoMotor(servo_pin_2)
        self.link1 = link1_length
        self.link2 = link2_length

    def inverse_kinematics(self, x, z):
        try:
            # Bereken de hoeken met behulp van inverse kinematica
            cos_angle2 = (x**2 + z**2 - self.link1**2 - self.link2**2) / (2 * self.link1 * self.link2)
            sin_angle2 = math.sqrt(1 - cos_angle2**2)  # Alleen de positieve wortel

            angle2 = math.atan2(sin_angle2, cos_angle2)
            k1 = self.link1 + self.link2 * cos_angle2
            k2 = self.link2 * sin_angle2

            angle1 = math.atan2(z, x) - math.atan2(k2, k1)

            # Converteer radianen naar graden
            angle1 = math.degrees(angle1)
            angle2 = math.degrees(angle2)

            return angle1, angle2
        except ValueError as e:
            print(f"Error calculating angles for x={x}, z={z}: {e}")
            return None, None

    def move_to_position(self, x, z):
        angle1, angle2 = self.inverse_kinematics(x, z)
        if angle1 is not None and angle2 is not None:
            self.servo1.move_to_angle(angle1)
            self.servo2.move_to_angle(angle2)

    def reset(self):
        self.servo1.move_to_angle(0)
        self.servo2.move_to_angle(0)

# Voorbeeld van hoe de klassen gebruikt kunnen worden
if __name__ == "__main__":
    # Initialiseer de SCARA robotarm
    scara_robot = SCARARobotArm(servo_pin_1=17, servo_pin_2=18, link1_length=10, link2_length=10)

    try:
        while True:
            # Beweeg de arm naar verschillende posities in het x, z vlak
            print("Beweeg naar positie 1 (x=10, z=10)")
            scara_robot.move_to_position(10, 10)
            sleep(2)
            
            print("Beweeg naar positie 2 (x=15, z=5)")
            scara_robot.move_to_position(15, 5)
            sleep(2)
            
            print("Beweeg naar positie 3 (x=5, z=15)")
            scara_robot.move_to_position(5, 15)
            sleep(2)

    except KeyboardInterrupt:
        print("Programma gestopt")
        scara_robot.reset()
