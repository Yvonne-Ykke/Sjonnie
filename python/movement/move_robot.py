from enum import Enum
from robot_arm import RobotArm
import angle_calculator as ac
import time

class RobotAction(Enum):
    MOVE = "move"
    GRIPPER_OPEN = "gripper_open"
    GRIPPER_CLOSE = "gripper_close"
    WRIST_ROTATE = "wrist_rotate"
    GRIPPER_UP = "gripper_up"
    GRIPPER_DOWN = "gripper_down"

def move():
    POS_1_X, POS_1_Y = 0, 400
    shoulder_angle, elbow_angle = ac.main(POS_1_X, POS_1_Y)
    WRIST_ANGLE_1 = 45

    RobotArm.gripper_open()
    RobotArm.gripper_up()
    RobotArm.move_to_position(shoulder_angle, elbow_angle, WRIST_ANGLE_1)

    time.sleep(5)

    RobotArm.gripper_down()
    time.sleep(5)

    RobotArm.gripper_close()
    RobotArm.gripper_up()

    POS_2_X, POS_2_Y = 300, 100
    shoulder_angle, elbow_angle = ac.main(POS_2_X, POS_2_Y)
    WRIST_ANGLE_2 = 90

    RobotArm.move_to_position(shoulder_angle, elbow_angle, WRIST_ANGLE_2)

    time.sleep(3)

    RobotArm.gripper_down()
    RobotArm.gripper_open()
