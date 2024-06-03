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

def inverse_kinematics(target_x, target_y, arm_length1, arm_length2):
    """
    Bereken de inverse kinematica voor een 2D twee-gewricht arm.
    
    Parameters:
    target_x (float): x-coördinaat van het doelpunt
    target_y (float): y-coördinaat van het doelpunt
    arm_length1 (float): lengte van het eerste segment van de arm
    arm_length2 (float): lengte van het tweede segment van de arm
    
    Returns:
    tuple: hoeken theta1 en theta2 in graden
    """
    
    # Bereken de afstand van de basis naar het doelpunt
    distance_to_target = math.sqrt(target_x**2 + target_y**2)
    
    # Controleer of het punt bereikbaar is
    if distance_to_target > (arm_length1 + arm_length2):
        raise ValueError("Het punt is niet bereikbaar.")
    
    # Bereken de hoek voor het tweede gewricht (theta2)
    cos_angle_joint2 = (target_x**2 + target_y**2 - arm_length1**2 - arm_length2**2) / (2 * arm_length1 * arm_length2)
    sin_angle_joint2 = math.sqrt(1 - cos_angle_joint2**2)  # Alleen de positieve oplossing overwegen
    angle_joint2 = math.atan2(sin_angle_joint2, cos_angle_joint2)
    
    # Bereken de hoek voor het eerste gewricht (theta1)
    intermediate_x = arm_length1 + arm_length2 * cos_angle_joint2
    intermediate_y = arm_length2 * sin_angle_joint2
    angle_joint1 = math.atan2(target_y, target_x) - math.atan2(intermediate_y, intermediate_x)
    
    # Converteer radialen naar graden
    angle_joint1_degrees = math.degrees(angle_joint1) 
    angle_joint2_degrees = math.degrees(angle_joint2) 
    
    # Pas de hoek van het eerste gewricht aan, zodat 90 graden = 0 graden
    
    return angle_joint1_degrees, angle_joint2_degrees

def radians_to_degrees(radians):
    return radians * 180 / np.pi

def convert_shoulder_angle_to_servo(shoulder_angle):
    	return -(shoulder_angle + 90) % 360 - 180

def is_blind_spot(shoulder_angle, elbow_angle):
    shoulder_angle_deg = convert_shoulder_angle_to_servo(shoulder_angle)
    return (-150 <= shoulder_angle_deg <= 150) and (-150 <= elbow_angle <= 150)

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
    
    try:
        shoulder_angle, elbow_angle = inverse_kinematics(x, y, ARM_SEGMENT_LENGTH, ARM_SEGMENT_LENGTH)
    except ValueError:
        return TargetStatus(x, y, None, None, Status.OUT_OF_REACH)
    
    if is_blind_spot(shoulder_angle, elbow_angle):
        return TargetStatus(x, y, shoulder_angle, elbow_angle, Status.REACHABLE)
    else:
        return TargetStatus(x, y, None, None, Status.BLIND_SPOT)

def main(x, y):
    return process_target(x, y)

def on_hover(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        target_status = process_target(x, y)
        tooltip_text = f"x={x:.1f}, y={y:.1f}, ({target_status.status.value}), ({convert_shoulder_angle_to_servo(target_status.servo_angle_1):.1f}, ({target_status.servo_angle_2:.1f})"
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
        print(f"Clicked on: x={x:.1f}, y={y:.1f}, Status: {target_status.status.value}")
        if target_status.status == Status.REACHABLE: 
            print(f"Servo Angle 1: {convert_shoulder_angle_to_servo(target_status.servo_angle_1)}, Servo Angle 2: {target_status.servo_angle_2}")
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
        tooltip_text = f"x={x:.1f}, y={y:.1f} ({convert_shoulder_angle_to_servo(target_status.servo_angle_1):.1f}, {target_status.servo_angle_2:.1f}) ({target_status.status.value})"
        annot1.xy = (x, y)
        annot1.set_text(tooltip_text)
        annot1.get_bbox_patch().set_facecolor("lightgray" if target_status.status == Status.REACHABLE else "red")
        annot1.get_bbox_patch().set_alpha(0.8)
        annot1.set_visible(True)
    else:
        annot1.set_visible(False)
        annot2.set_visible(False)

plot()
