import math
import numpy as np
import matplotlib.pyplot as plt
import controller

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

def calculate_valid_angles(x, y):
    global prev_elbow_angle, prev_shoulder_angle
    if point_hits_robot_base(x, y) or point_is_out_of_reach(x, y, SEGMENT_LENGTH): return None, None
    shoulder_angle, elbow_angle = calculate_arm_angles(x, y, SEGMENT_LENGTH, prev_shoulder_angle, prev_elbow_angle)
    prev_elbow_angle = elbow_angle
    prev_shoulder_angle = shoulder_angle

    return shoulder_angle, elbow_angle

