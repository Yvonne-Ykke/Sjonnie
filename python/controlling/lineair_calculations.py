import pygame
import time
import math
from pypot.dynamixel import Dxl320IO

#pip install gpiozero
#pip install pypot
#pip install pygame

class AX12Motor:
    def __init__(self, motor_id, dxl_io):
        self.id = motor_id
        self.dxl_io = dxl_io

    def move_to_position(self, position):
        self.dxl_io.set_goal_position({self.id: position})

class RobotArm:
    def __init__(self, dxl_io, motor_ids, link1_length, link2_length):
        self.dxl_io = dxl_io
        self.motors = [AX12Motor(motor_id, dxl_io) for motor_id in motor_ids]
        self.link1 = link1_length
        self.link2 = link2_length

    def inverse_kinematics(self, x, y):
        try:
            # Bereken de hoeken met behulp van inverse kinematica
            cos_angle2 = (x**2 + y**2 - self.link1**2 - self.link2**2) / (2 * self.link1 * self.link2)
            sin_angle2 = math.sqrt(1 - cos_angle2**2)
            angle2 = math.atan2(sin_angle2, cos_angle2)
            k1 = self.link1 + self.link2 * cos_angle2
            k2 = self.link2 * sin_angle2
            angle1 = math.atan2(y, x) - math.atan2(k2, k1)
            angle1 = math.degrees(angle1)
            angle2 = math.degrees(angle2)
            return angle1, angle2
        except ValueError as e:
            print(f"Error calculating angles for x={x}, y={y}: {e}")
            return None, None

    def move_to_position(self, x, y):
        angle1, angle2 = self.inverse_kinematics(x, y)
        if angle1 is not None and angle2 is not None:
            self.motors[0].move_to_position(angle1)
            self.motors[1].move_to_position(angle2)

    def reset(self):
        for motor in self.motors:
            motor.move_to_position(0)

def initialize_joystick():
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick

def get_joystick_input(joystick):
    pygame.event.pump()
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)
    return x_axis, y_axis

if __name__ == "__main__":
    # Connect to the motors
    with Dxl320IO('/dev/ttyUSB0', baudrate=1000000) as dxl_io:
        # Initialize the SCARA robot arm
        motor_ids = [1, 2]  # IDs van de servomotoren
        scara_robot = RobotArm(dxl_io, motor_ids, link1_length=10, link2_length=10)

        # Initialize the joystick
        joystick = initialize_joystick()

        try:
            while True:
                # Read joystick input
                x_input, y_input = get_joystick_input(joystick)

                # Scale the joystick input to the workspace of the robot arm
                x = x_input * 10  # Assuming the workspace x is between -10 and 10
                y = y_input * 10  # Assuming the workspace y is between -10 and 10

                # Move the robot arm based on joystick input
                scara_robot.move_to_position(x, y)
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Programma gestopt")
            scara_robot.reset()
            pygame.quit()
