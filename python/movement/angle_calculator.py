import math
import numpy as np
import matplotlib.pyplot as plt
import controller
from movement import controller

# Parameters
SEGMENT_LENGTH = 300.0
AX12_SHOULDER_MIN_ANGLE = -130
AX12_SHOULDER_MAX_ANGLE = 130
AX12_ELBOW_MIN_ANGLE = -150
AX12_ELBOW_MAX_ANGLE = 150
FORBIDDEN_RADIUS = 250.0
DOTS_PRECISION = 200
prev_elbow_angle = 0
prev_shoulder_angle = 0

# Generate reachable coordinates
shoulder_angles = np.radians(np.linspace(AX12_SHOULDER_MIN_ANGLE, AX12_SHOULDER_MAX_ANGLE, DOTS_PRECISION))  # Fine discretization
elbow_angles = np.radians(np.linspace(AX12_ELBOW_MIN_ANGLE, AX12_ELBOW_MAX_ANGLE, DOTS_PRECISION))     # Fine discretization
# Generate all possible combinations of shoulder and elbow angles
reachable_coordinates = [(SEGMENT_LENGTH * (np.cos(shoulder_angle) + np.cos(shoulder_angle + elbow_angle)),
                          SEGMENT_LENGTH * (np.sin(shoulder_angle) + np.sin(shoulder_angle + elbow_angle)))
                         for shoulder_angle in shoulder_angles
                         for elbow_angle in elbow_angles]


x_reach, y_reach = zip(*reachable_coordinates)
# Check if the point is within the robot's reach
def point_is_out_of_reach(x, y, arm_segment_length):
    if distance_from_origin(x, y) > 2 * arm_segment_length:
         return True
    # Check the shortes angle using current position
def choice(shoulder_angle1, elbow_angle1, shoulder_angle2, elbow_angle2, current_pos_shoulder, current_pos_elbow): 
    # Calculate the angular distance between the current position and the target position for both solutions
    diff_a = abs(current_pos_shoulder - convert_to_servo_angle(shoulder_angle1)) + abs(current_pos_elbow - elbow_angle1)
    diff_b = abs(current_pos_shoulder - convert_to_servo_angle(shoulder_angle2)) + abs(current_pos_elbow - elbow_angle2)
    # Choose the solution with the smallest angular distance
    if diff_a <= diff_b:
        return shoulder_angle1, elbow_angle1
    else:
        return shoulder_angle2, elbow_angle2
    
def calculate_arm_angles(x, y, segment_length, current_pos_shoulder, current_pos_elbow):
    # Calculate elbow angle for the first solution
    cos_angle_elbow = (x**2 + y**2 - segment_length**2 - segment_length**2) / (2 * segment_length * segment_length)
    sin_angle_elbow = math.sqrt(1 - cos_angle_elbow**2)
    elbow_angle = math.atan2(sin_angle_elbow, cos_angle_elbow)
    shoulder_angle = math.atan2(y, x) - math.atan2(segment_length * sin_angle_elbow, segment_length + segment_length * cos_angle_elbow)
    shoulder_angle_degrees = math.degrees(shoulder_angle)
    elbow_angle_degrees = math.degrees(elbow_angle)
    blind_spot_1 = not is_shoulder_in_range(convert_to_servo_angle(shoulder_angle_degrees)) and is_elbow_in_range(elbow_angle_degrees)
# Calculate elbow angle for the second solution
    sin_angle_elbow_other = -sin_angle_elbow
    elbow_angle_other = math.atan2(sin_angle_elbow_other, cos_angle_elbow)
    shoulder_angle_other = math.atan2(y, x) - math.atan2(segment_length * sin_angle_elbow_other, segment_length + segment_length * cos_angle_elbow)
    shoulder_angle_other_degrees = math.degrees(shoulder_angle_other)
    elbow_angle_other_degrees = math.degrees(elbow_angle_other)
    blind_spot_2 = not is_shoulder_in_range(convert_to_servo_angle(shoulder_angle_other_degrees)) and is_elbow_in_range(elbow_angle_other_degrees)
    # Determine which solution to use based on blind spots
    if blind_spot_1 and blind_spot_2:
        print("Blind spot found")
        return None
    elif blind_spot_1:
        print("Blind spot 1 found")
        return shoulder_angle_other_degrees, elbow_angle_other_degrees
        
    elif blind_spot_2:
        print("Blind spot 2 found")
        return shoulder_angle_degrees, elbow_angle_degrees
    else:
        # Use choice function to determine the closest angle
        return choice(shoulder_angle_degrees, elbow_angle_degrees, shoulder_angle_other_degrees, elbow_angle_other_degrees, current_pos_shoulder, current_pos_elbow)
    
def radians_to_degrees(radians): return radians * 180 / np.pi
def is_shoulder_in_range(angle): return -130 <= angle <= 130
def is_elbow_in_range(angle): return -150 <= angle <= 150
def point_hits_robot_base(x, y): return distance_from_origin(x, y) <= FORBIDDEN_RADIUS
def convert_to_servo_angle(angle): return -(angle + 90) % 360 - 180
def is_in_range(angle): return -150 <= angle <= 150
def is_valid_angle(angle): return is_in_range(angle)
def distance_from_origin(x, y): return np.sqrt(x ** 2 + y ** 2)

def main(x, y):
    shoulder_angle, elbow_angle = calculate_valid_angles(x, y)
    if (shoulder_angle is not None) and (elbow_angle is not None):
        print(f"Angles: {shoulder_angle:.1f}, {elbow_angle:.1f}")
        controller.move_servos(convert_to_servo_angle(shoulder_angle), elbow_angle)
        return shoulder_angle, elbow_angle
    else:
        print("Invalid position")
        return None, None
# Calculate the valid angles for the given target position
def calculate_valid_angles(x, y):
    global prev_elbow_angle, prev_shoulder_angle
    if point_hits_robot_base(x, y) or point_is_out_of_reach(x, y, SEGMENT_LENGTH): return None, None
    shoulder_angle, elbow_angle = calculate_arm_angles(x, y, SEGMENT_LENGTH, prev_shoulder_angle, prev_elbow_angle)
    prev_elbow_angle = elbow_angle
    prev_shoulder_angle = shoulder_angle

    return shoulder_angle, elbow_angle


def on_hover(event):
    # Check if the mouse is inside the plot
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
        # Get the x and y coordinates of the click
        x, y = event.xdata, event.ydata
        shoulder_angle, elbow_angle = calculate_valid_angles(x, y)
        # If the angles are valid, move the arm to the new position
        if (shoulder_angle is not None) and (elbow_angle is not None):
            shoulder_angle_servo = convert_to_servo_angle(shoulder_angle)
            controller.move_servos(shoulder_angle_servo, -elbow_angle)

            print(f"Angles: {shoulder_angle_servo:.1f}, {elbow_angle:.1f}")
            # Convert angles to radians
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
#plot()
