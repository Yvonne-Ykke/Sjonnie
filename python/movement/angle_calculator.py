import math
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from functools import lru_cache

# Parameters
SEGMENT_LENGTH = 300.0
AX12_MIN_ANGLE = -150
AX12_MAX_ANGLE = 150
FORBIDDEN_RADIUS = 150.0
DOTS_PRECISION = 200

# Generate reachable coordinates
shoulder_angles = np.radians(np.linspace(AX12_MIN_ANGLE, AX12_MAX_ANGLE, DOTS_PRECISION))  # Fine discretization
elbow_angles = np.radians(np.linspace(AX12_MIN_ANGLE, AX12_MAX_ANGLE, DOTS_PRECISION))     # Fine discretization

reachable_coordinates = [(SEGMENT_LENGTH * (np.cos(shoulder_angle) + np.cos(shoulder_angle + elbow_angle)),
                          SEGMENT_LENGTH * (np.sin(shoulder_angle) + np.sin(shoulder_angle + elbow_angle)))
                         for shoulder_angle in shoulder_angles
                         for elbow_angle in elbow_angles]


x_reach, y_reach = zip(*reachable_coordinates)

def point_is_out_of_reach(x, y, arm_segment_length):
    if distance_from_origin(x, y) > 2 * arm_segment_length:
         return True
    
def calculate_arm_angles(x, y, segment_length):
    cos_angle_elbow = (x**2 + y**2 - segment_length**2 - segment_length**2) / (2 * segment_length * segment_length)
    sin_angle_elbow = math.sqrt(1 - cos_angle_elbow**2)
    if x < 0 and y < 0:  # Select appropriate solution
        sin_angle_elbow = -sin_angle_elbow
    elbow_angle = math.atan2(sin_angle_elbow, cos_angle_elbow)

    shoulder_angle = math.atan2(y, x) - math.atan2(segment_length * sin_angle_elbow, segment_length + segment_length * cos_angle_elbow)

    shoulder_angle_degrees = math.degrees(shoulder_angle)
    elbow_angle_degrees = math.degrees(elbow_angle)

    if distance_from_origin(x, y) > 2 * segment_length:
        return shoulder_angle_degrees, elbow_angle_degrees

    if x < 0:
        cos_angle_elbow_other = (x**2 + y**2 - segment_length**2 - segment_length**2) / (2 * segment_length * segment_length)
        sin_angle_elbow_other = math.sqrt(1 - cos_angle_elbow_other**2)
        if y > 0:  # Select appropriate solution
            sin_angle_elbow_other = -sin_angle_elbow_other
        elbow_angle_other = math.atan2(sin_angle_elbow_other, cos_angle_elbow_other)
        shoulder_angle_other = math.atan2(y, x) - math.atan2(segment_length * sin_angle_elbow_other, segment_length + segment_length * cos_angle_elbow_other)
        return math.degrees(shoulder_angle_other), math.degrees(elbow_angle_other)
    elif x > 0 and y < 0:
        cos_angle_elbow_other = (x**2 + y**2 - segment_length**2 - segment_length**2) / (2 * segment_length * segment_length)
        sin_angle_elbow_other = math.sqrt(1 - cos_angle_elbow_other**2)
        sin_angle_elbow_other = -sin_angle_elbow_other
        elbow_angle_other = math.atan2(sin_angle_elbow_other, cos_angle_elbow_other)
        shoulder_angle_other = math.atan2(y, x) - math.atan2(segment_length * sin_angle_elbow_other, segment_length + segment_length * cos_angle_elbow_other)
        return math.degrees(shoulder_angle_other), math.degrees(elbow_angle_other)
    else:
        return shoulder_angle_degrees, elbow_angle_degrees

def radians_to_degrees(radians): return radians * 180 / np.pi
def is_in_range(angle): return -150 <= angle <= 150
def point_hits_robot_base(x, y): return distance_from_origin(x, y) <= FORBIDDEN_RADIUS
def convert_to_servo_angle(angle): return -(angle + 90) % 360 - 180
def is_in_range(angle): return -150 <= angle <= 150
def is_valid_angle(angle): return is_in_range(angle)
def distance_from_origin(x, y): return np.sqrt(x ** 2 + y ** 2)

def main(x, y):
    return calculate_valid_angles(x, y)

def calculate_valid_angles(x, y):
    if point_hits_robot_base(x, y) or point_is_out_of_reach(x, y, SEGMENT_LENGTH): return None, None

    shoulder_angle, elbow_angle = calculate_arm_angles(x, y, SEGMENT_LENGTH)
    
    if is_valid_angle(convert_to_servo_angle(shoulder_angle)) and is_valid_angle(elbow_angle):
        return shoulder_angle, elbow_angle
    return None, None

def on_hover(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        tooltip_text = f"x={x:.1f}, y={y:.1f}"
        annot1.xy = (x, y)
        annot1.set_text(tooltip_text)
        annot1.get_bbox_patch().set_facecolor("lightgray")
        annot1.get_bbox_patch().set_alpha(0.8)
        annot1.set_visible(True)
    else:
        annot1.set_visible(False)

def on_click(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        shoulder_angle, elbow_angle = calculate_valid_angles(x, y)

        if (shoulder_angle is not None) and (elbow_angle is not None):
            shoulder_angle_servo = convert_to_servo_angle(shoulder_angle)
            print(f"Angles: {shoulder_angle_servo:.1f}, {elbow_angle:.1f}")
        
            shoulder_angle_rad = np.radians(shoulder_angle)
            elbow_angle_rad = np.radians(elbow_angle)

            # Calculate coordinates of the arm segments
            upper_arm_end_x = SEGMENT_LENGTH * np.cos(shoulder_angle_rad)
            upper_arm_end_y = SEGMENT_LENGTH * np.sin(shoulder_angle_rad)

            lower_arm_end_x = upper_arm_end_x + SEGMENT_LENGTH * np.cos(shoulder_angle_rad + elbow_angle_rad)
            lower_arm_end_y = upper_arm_end_y + SEGMENT_LENGTH * np.sin(shoulder_angle_rad + elbow_angle_rad)

            # Update the plot with new arm positions
            arm1_line.set_data([0, upper_arm_end_x], [0, upper_arm_end_y])
            arm2_line.set_data([upper_arm_end_x, lower_arm_end_x], [upper_arm_end_y, lower_arm_end_y])
            fig.canvas.draw_idle()
            
def plot():
    global fig, ax, arm1_line, arm2_line, annot1, annot2
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(y_reach, x_reach, 'b.', markersize=1, label="Reachable Coordinates")
    ax.set(xlabel="y (mm)", ylabel="x (mm)", title="Reachable Coordinates of the Robot Arm (Reversed Axes)", aspect='equal')
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
plot()
