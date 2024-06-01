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

reachable_coordinates = [(ARM_SEGMENT_LENGTH * np.cos(shoulder_angle) + ARM_SEGMENT_LENGTH * np.cos(shoulder_angle + elbow_angle),
                          ARM_SEGMENT_LENGTH * np.sin(shoulder_angle) + ARM_SEGMENT_LENGTH * np.sin(shoulder_angle + elbow_angle))
                         for shoulder_angle in shoulder_angles
                         for elbow_angle in elbow_angles]

x_reach, y_reach = zip(*reachable_coordinates)

def calculate_angle_from_coordinates(x, y):
    return np.arctan2(y, x)

def law_of_cosines(a, b, c):
    try:
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        return np.arccos(np.clip(cos_C, -1.0, 1.0))
    except ValueError:
        return float('nan')

def distance(x, y):
    return np.sqrt(x**2 + y**2)

def calculate_arm_angles(target_x, target_y):
    dist = np.sqrt(target_x ** 2 + target_y ** 2)
    if dist > 2 * ARM_SEGMENT_LENGTH:
        return None, None

    cos_elbow_angle = (2 * ARM_SEGMENT_LENGTH ** 2 - dist ** 2) / (2 * ARM_SEGMENT_LENGTH ** 2)
    cos_elbow_angle = np.clip(cos_elbow_angle, -1, 1)
    elbow_angle = np.arccos(cos_elbow_angle)

    shoulder_angle = np.arctan2(target_y, target_x) - np.arctan2(ARM_SEGMENT_LENGTH * np.sin(elbow_angle), ARM_SEGMENT_LENGTH + ARM_SEGMENT_LENGTH * np.cos(elbow_angle))

    if target_x < 0:
        if target_y >= 0:
            shoulder_angle = np.pi - shoulder_angle  # Second quadrant
        else:
            shoulder_angle = -(np.pi - abs(shoulder_angle))  # Third quadrant

    if -150 <= np.degrees(shoulder_angle) <= 150 and -150 <= np.degrees(elbow_angle) <= 150:
        return np.degrees(shoulder_angle), np.degrees(elbow_angle)
    else:
        return None, None

def radians_to_degrees(radians):
    return radians * 180 / np.pi

def is_blind_spot(shoulder_angle, elbow_angle):
    shoulder_angle_deg = radians_to_degrees(shoulder_angle)
    elbow_angle_deg = radians_to_degrees(elbow_angle)
    return (-150 <= shoulder_angle_deg <= 150) and (-150 <= elbow_angle_deg <= 150)

def is_forbidden_area(x, y):
    return distance(x, y) <= FORBIDDEN_RADIUS

def convert_angle_for_servo(angle):
    return angle

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
    
    shoulder_angle, elbow_angle = calculate_arm_angles(x, y)
    if shoulder_angle is None or elbow_angle is None:
        return TargetStatus(x, y, None, None, Status.OUT_OF_REACH)
    
    if not is_blind_spot(shoulder_angle, elbow_angle):
        servo_angle_1, servo_angle_2 = convert_angle_for_servo(radians_to_degrees(shoulder_angle)), convert_angle_for_servo(radians_to_degrees(elbow_angle))
        return TargetStatus(x, y, servo_angle_1, servo_angle_2, Status.REACHABLE)
    else:
        return TargetStatus(x, y, None, None, Status.BLIND_SPOT)

def main(x, y):
    return process_target(x, y)

def on_hover(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        tooltip_text = f"x={x:.1f}, y={y:.1f} ({target_status.status.value})"
        annot.xy = (x, y)
        annot.set_text(tooltip_text)
        annot.get_bbox_patch().set_facecolor("lightgray" if target_status.status == Status.REACHABLE else "red")
        annot.get_bbox_patch().set_alpha(0.8)
        annot.set_visible(True)
    else:
        annot.set_visible(False)

def on_click(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        print(f"Clicked on: x={x:.1f}, y={y:.1f}, Status: {target_status.status.value}")
        if target_status.status == Status.REACHABLE:
            print(f"Servo Angle 1: {target_status.servo_angle_1}, Servo Angle 2: {target_status.servo_angle_2}")

def plot():
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

    # Calculate coordinates for arms
    arm1_end_x = ARM_SEGMENT_LENGTH * np.cos(np.radians(AX12_MIN_ANGLE))
    arm1_end_y = ARM_SEGMENT_LENGTH * np.sin(np.radians(AX12_MIN_ANGLE))

    arm2_start_x = arm1_end_x
    arm2_start_y = arm1_end_y

    arm2_end_x = arm2_start_x + ARM_SEGMENT_LENGTH * np.cos(np.radians(AX12_MAX_ANGLE))
    arm2_end_y = arm2_start_y + ARM_SEGMENT_LENGTH * np.sin(np.radians(AX12_MAX_ANGLE))

      # Plot the two arms
    ax.plot([0, arm1_end_x], [0, arm1_end_y], 'r-', linewidth=2, label='Arm 1')
    ax.plot([arm2_start_x, arm2_end_x], [arm2_start_y, arm2_end_y], 'r-', linewidth=2, label='Arm 2')

    cid_click = fig.canvas.mpl_connect('button_press_event', on_click)
    cid_hover = fig.canvas.mpl_connect('motion_notify_event', on_hover)

    global annot
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def hover(event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            target_status = process_target(x, y)
            update_annot(x, y, target_status.status)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            annot.set_visible(False)
        fig.canvas.draw()

    def update_annot(x, y, status):
        annot.xy = (x, y)
        text = f"x={x:.1f}, y={y:.1f} ({status.value})"
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor("white" if status == Status.REACHABLE else "red")
        annot.get_bbox_patch().set_alpha(0.8)

    fig.canvas.mpl_connect("motion_notify_event", hover)
    plt.show()

    fig.canvas.mpl_disconnect(cid_hover)
    fig.canvas.mpl_disconnect(cid_click)

plot()
