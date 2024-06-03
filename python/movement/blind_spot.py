import math
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

# Parameters
ARM_SEGMENT_LENGTH = 300.0
AX12_MIN_ANGLE = -150
AX12_MAX_ANGLE = 150
FORBIDDEN_RADIUS = 150.0
DOTS_PRECISION = 200

# Generate reachable coordinates
shoulder_angles = np.radians(np.linspace(AX12_MIN_ANGLE, AX12_MAX_ANGLE, DOTS_PRECISION))  # Fine discretization
elbow_angles = np.radians(np.linspace(AX12_MIN_ANGLE, AX12_MAX_ANGLE, DOTS_PRECISION))     # Fine discretization

reachable_coordinates =[(ARM_SEGMENT_LENGTH * np.cos(shoulder_angle) + ARM_SEGMENT_LENGTH * np.cos(shoulder_angle + elbow_angle),
                          ARM_SEGMENT_LENGTH * np.sin(shoulder_angle) + ARM_SEGMENT_LENGTH * np.sin(shoulder_angle + elbow_angle))
                         for shoulder_angle in shoulder_angles
                         for elbow_angle in elbow_angles]

x_reach, y_reach = zip(*reachable_coordinates)

def distance(x, y):
    return np.sqrt(x**2 + y**2)

def inverse_kinematics(target_x, target_y, arm_segment_length):
    # Calculate the distance from the base to the target point
    distance_to_target = math.sqrt(target_x**2 + target_y**2)
    if distance_to_target > 2 * arm_segment_length:
        raise ValueError("The target point is not reachable.")

    # Calculate the angle for the second joint (theta2)
    cos_angle_joint2 = (target_x**2 + target_y**2 - arm_segment_length**2 - arm_segment_length**2) / (2 * arm_segment_length * arm_segment_length)
    sin_angle_joint2 = math.sqrt(1 - cos_angle_joint2**2)
    if target_x < 0 and target_y < 0:  # Passende oplossing selecteren
        sin_angle_joint2 = -sin_angle_joint2
    angle_joint2 = math.atan2(sin_angle_joint2, cos_angle_joint2)

    # Calculate the angle for the first joint (theta1)
    angle_joint1 = math.atan2(target_y, target_x) - math.atan2(arm_segment_length * sin_angle_joint2, arm_segment_length + arm_segment_length * cos_angle_joint2)

    # Convert radians to degrees
    angle_joint1_degrees = math.degrees(angle_joint1)
    angle_joint2_degrees = math.degrees(angle_joint2)

    # Check if the arm can come to rest on the right side
    if target_x > 0:
        # Calculate the angle for the second joint (theta2) for the other possible position
        cos_angle_joint2_other = (target_x**2 + target_y**2 - arm_segment_length**2 - arm_segment_length**2) / (2 * arm_segment_length * arm_segment_length)
        sin_angle_joint2_other = math.sqrt(1 - cos_angle_joint2_other**2)
        if target_x > 0 and target_y > 0:  # Passende oplossing selecteren
            sin_angle_joint2_other = -sin_angle_joint2_other
        angle_joint2_other = math.atan2(sin_angle_joint2_other, cos_angle_joint2_other)

        # Calculate the angle for the first joint (theta1) for the other possible position
        angle_joint1_other = math.atan2(target_y, target_x) - math.atan2(arm_segment_length * sin_angle_joint2_other, arm_segment_length + arm_segment_length * cos_angle_joint2_other)

        # Convert radians to degrees
        angle_joint1_other_degrees = math.degrees(angle_joint1_other)
        angle_joint2_other_degrees = math.degrees(angle_joint2_other)

        # Return the closest solution
        if distance_to_target > 2 * arm_segment_length:
            return angle_joint1_degrees, angle_joint2_degrees
        else:
            return angle_joint1_other_degrees, angle_joint2_other_degrees
    else:
        return angle_joint1_degrees, angle_joint2_degrees


def map_to_servo(shoulder_angle):
    	return -(shoulder_angle + 90) % 360 - 180

def radians_to_degrees(radians):
    return radians * 180 / np.pi

def map_to_servo(angle):
    return -(angle + 90) % 360 - 180

def within_angle_range(angle):
    return -150 <= angle <= 150

def are_valid_angles(shoulder_angle, elbow_angle):
    shoulder_servo_angle = map_to_servo(shoulder_angle)
    print(f"origneel: {shoulder_angle:.1f}, {elbow_angle:.1f}")
    print(f"Servo:: {shoulder_servo_angle:.1f}, elbow_angle: {elbow_angle:.1f}")
    return within_angle_range(shoulder_servo_angle) and within_angle_range(elbow_angle)

def is_forbidden_area(x, y):
    return distance(x, y) <= FORBIDDEN_RADIUS


class Status(Enum):
    FORBIDDEN_AREA = "Forbidden area"
    OUT_OF_REACH = "Out of reach"
    REACHABLE = "Reachable"
    BLIND_SPOT = "Blind spot"

class TargetStatus:
    def __init__(self, x, y, servo_angle_1, servo_angle_2, status):
        self.x = x
        self.y = y
        self.servo_angle_1 = servo_angle_1
        self.servo_angle_2 = servo_angle_2
        self.status = status


def process_target(x, y):
    if is_forbidden_area(x, y):
        return TargetStatus(x, y, None, None, Status.FORBIDDEN_AREA)
    
    try:
        shoulder_angle, elbow_angle = inverse_kinematics(x, y, ARM_SEGMENT_LENGTH)
    except ValueError:
        return TargetStatus(x, y, None, None, Status.OUT_OF_REACH)
    
    are_valid_angles2 = are_valid_angles(shoulder_angle, elbow_angle)
    if are_valid_angles2:
        return TargetStatus(x, y, shoulder_angle, elbow_angle, Status.REACHABLE)
    else:
        print(" NO Valid angles!")
        return TargetStatus(x, y, None, None, Status.BLIND_SPOT)

def main(x, y):
    return process_target(x, y)

def on_hover(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        tooltip_text = f"x={x:.1f}, y={y:.1f}, ({target_status.status.value}), ({map_to_servo(target_status.servo_angle_1):.1f}, ({target_status.servo_angle_2:.1f})"
        annot1.xy = (x, y)
        annot1.set_text(tooltip_text)
        annot1.get_bbox_patch().set_facecolor("lightgray" if target_status.status == Status.REACHABLE else "red")
        annot1.get_bbox_patch().set_alpha(0.8)
        annot1.set_visible(True)
    else:
        annot1.set_visible(False)

def on_click(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        if target_status.status == Status.REACHABLE: 
            print(f"Angles: {map_to_servo(target_status.servo_angle_1):.1f}, {target_status.servo_angle_2:.1f}")
        # Update arm positions based on calculated angles
        if target_status.status == Status.REACHABLE:
            shoulder_angle_rad = np.radians(target_status.servo_angle_1)
            elbow_angle_rad = np.radians(target_status.servo_angle_2)

            # Calculate coordinates of the arm segments
            arm1_end_x = ARM_SEGMENT_LENGTH * np.cos(shoulder_angle_rad)
            arm1_end_y = ARM_SEGMENT_LENGTH * np.sin(shoulder_angle_rad)

            arm2_end_x = arm1_end_x + ARM_SEGMENT_LENGTH * np.cos(shoulder_angle_rad + elbow_angle_rad)
            arm2_end_y = arm1_end_y + ARM_SEGMENT_LENGTH * np.sin(shoulder_angle_rad + elbow_angle_rad)

            # Update the plot with new arm positions
            arm1_line.set_data([0, arm1_end_x], [0, arm1_end_y])
            arm2_line.set_data([arm1_end_x, arm2_end_x], [arm1_end_y, arm2_end_y])
            fig.canvas.draw_idle()
            

def plot():
    global fig, ax, arm1_line, arm2_line, annot1, annot2
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(y_reach, x_reach, 'b.', markersize=1, label="Reachable Coordinates")
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("x (mm)")
    ax.set_title("Reachable Coordinates of the Robot Arm (Reversed Axes)")
    ax.grid(True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.legend()
    ax.axis('equal')

    # Initialize arm lines
    arm1_line, = ax.plot([0, 0], [0, 0], 'r-', linewidth=2, label='Arm 1')
    arm2_line, = ax.plot([0, 0], [0, 0], 'r-', linewidth=2, label='Arm 2')

    cid_click = fig.canvas.mpl_connect('button_press_event', on_click)
    cid_hover = fig.canvas.mpl_connect('motion_notify_event', on_hover)

    annot1 = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot1.set_visible(False)
    
    annot2 = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="lightblue", alpha=0.5),
                        arrowprops=dict(arrowstyle="->"))
    annot2.set_visible(False)

    plt.show()

    fig.canvas.mpl_disconnect(cid_hover)
    fig.canvas.mpl_disconnect(cid_click)

def on_hover(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        tooltip_text = f"x={x:.1f}, y={y:.1f} ({target_status.status.value})"
        annot1.xy = (x, y)
        annot1.set_text(tooltip_text)
        annot1.get_bbox_patch().set_facecolor("lightgray" if target_status.status == Status.REACHABLE else "red")
        annot1.get_bbox_patch().set_alpha(0.8)
        annot1.set_visible(True)
    else:
        annot1.set_visible(False)
        annot2.set_visible(False)

plot()
