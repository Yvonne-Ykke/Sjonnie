import math

# Constants for the lengths of the robot's arm segments
ARM_SEGMENT_LENGTH = 300.0
# Servo parameters
SERVO_MIN_ANGLE = -150
SERVO_MAX_ANGLE = 150

def calculate_angle_from_coordinates(x, y):
    """Calculate the angle in radians from coordinates."""
    return math.atan2(y, x)

def law_of_cosines(a, b, c):
    """Calculate angle C using the law of cosines."""
    if a == 0 or b == 0:
        return 0
    try:
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        cos_C = min(1, max(-1, cos_C))  # Clamp the value to avoid domain errors
        return math.acos(cos_C)
    except ValueError:
        return float('nan')

def distance(x, y):
    """Calculate the distance from the origin (0,0) to (x,y)."""
    return math.sqrt(x**2 + y**2)

def calculate_arm_angles(target_x, target_y):
    """Calculate the two sets of joint angles for given target_x and target_y."""
    dist = distance(target_x, target_y)
    if dist > 2 * ARM_SEGMENT_LENGTH:
        raise ValueError("Target is out of reach")

    elbow_angle = law_of_cosines(ARM_SEGMENT_LENGTH, ARM_SEGMENT_LENGTH, dist)
    shoulder_angle_part = calculate_angle_from_coordinates(target_x, target_y)
    shoulder_angle_part2 = law_of_cosines(ARM_SEGMENT_LENGTH, dist, ARM_SEGMENT_LENGTH)
    
    shoulder_angle1 = shoulder_angle_part + shoulder_angle_part2
    elbow_angle1 = elbow_angle
    shoulder_angle2 = shoulder_angle_part - shoulder_angle_part2
    elbow_angle2 = -elbow_angle
    
    return (shoulder_angle1, elbow_angle1), (shoulder_angle2, elbow_angle2)

def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * 180 / math.pi

def is_blind_spot(shoulder_angle, elbow_angle):
    """Check if the given angles are within the blind spot range."""
    shoulder_angle_deg = radians_to_degrees(shoulder_angle)
    elbow_angle_deg = radians_to_degrees(elbow_angle)
    return (-150 <= shoulder_angle_deg <= 150) and (-150 <= elbow_angle_deg <= 150)

def determine_best_angles(angles1, angles2, target_x, target_y):
    """Determine the better set of angles based on minimum angular movement."""
    angle1a_deg = radians_to_degrees(angles1[0])
    angle1b_deg = radians_to_degrees(angles2[0])
    angle2a_deg = radians_to_degrees(angles1[1])
    angle2b_deg = radians_to_degrees(angles2[1])

    diff_a = abs(angle1a_deg) + abs(angle2a_deg)
    diff_b = abs(angle1b_deg) + abs(angle2b_deg)

    return angles1 if diff_a <= diff_b else angles2

def convert_angle_for_servo(angle):
    """Convert angle from -150 to 150 degrees to servo range -150 to 150 degrees."""
    return angle

def process_target(target_x, target_y):
    """Process a single target coordinate."""
    try:
        shoulder_angles1, elbow_angles1, shoulder_angles2, elbow_angles2 = calculate_arm_angles(target_x, target_y)
        if not is_blind_spot(shoulder_angles1, elbow_angles1) and not is_blind_spot(shoulder_angles2, elbow_angles2):
            best_angles = determine_best_angles(shoulder_angles1, elbow_angles1, shoulder_angles2, elbow_angles2, target_x, target_y)
        elif not is_blind_spot(shoulder_angles1, elbow_angles1):
            best_angles = shoulder_angles1, elbow_angles1
        else:
            print("Blind spot detected")
            return None, None
        
        servo_angles = [convert_angle_for_servo(radians_to_degrees(angle)) for angle in best_angles]
        print(f"Servo 1: {servo_angles[0]:.1f}°, Servo 2: {servo_angles[1]:.1f}°")
        return servo_angles[0], servo_angles[1]
    except ValueError as e:
        print(f"x={target_x:.1f}, y={target_y:.1f}: {e}")
        return None, None

def main(x, y):
    """Main function to provide a coordinate and calculate servo angles."""
    return process_target(x, y)

if __name__ == "__main__":
    main(150, 150)
