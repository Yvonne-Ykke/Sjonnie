import math

# Constants for the lengths of the robot's arm segments
LEN1 = 300.0
LEN2 = 300.0
# Current position of the servos
POS1 = 0 
POS2 = 0

def law_of_cosines(a, b, c):
    if a == 0 or b == 0:
        return 0
    """Calculate angle C using the law of cosines."""
    try:
        # Ensure the value inside acos is within the valid range of [-1, 1]
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        cos_C = min(1, max(-1, cos_C))  # Clamp the value to avoid domain errors
        return math.acos(cos_C)
    except ValueError:
        return float('nan')

def distance(x, y):
    """Calculate the distance from the origin (0,0) to (x,y)."""
    return math.sqrt(x**2 + y**2)

def angles(target_x, target_y):
    """Calculate the two sets of joint angles for given target_x and target_y."""
    dist = distance(target_x, target_y)
    
    if dist > (LEN1 + LEN2):
        raise ValueError("Target is out of reach")
    
    # Calculate the angle at the elbow using the law of cosines
    elbow_angle = law_of_cosines(LEN1, LEN2, dist)
    
    # Calculate the shoulder angle for both configurations
    shoulder_angle_part = math.atan2(target_y, target_x)
    shoulder_angle_part2 = law_of_cosines(LEN1, dist, LEN2)
    
    # First set of angles
    shoulder_angle1 = shoulder_angle_part + shoulder_angle_part2
    elbow_angle1 = elbow_angle
    
    # Second set of angles (other solution)
    shoulder_angle2 = shoulder_angle_part - shoulder_angle_part2
    elbow_angle2 = -elbow_angle
    
    return (shoulder_angle1, elbow_angle1), (shoulder_angle2, elbow_angle2)

def deg(radians):
    """Convert radians to degrees."""
    return radians * 180 / math.pi

def blind_spot(shoulder_angle, elbow_angle):
    angle1a_deg = deg(shoulder_angle)  # shoulder angle a
    angle2a_deg = deg(elbow_angle)  # elbow angle a
    # Check if the shoulder and elbow do not have an angle they cannot make. If so, the object is unreachable
    if (-120 < angle1a_deg < -60 or -30 < angle2a_deg < 30):
        return True
    else:
        return False

def choice(shoulder_angle1, elbow_angle1, shoulder_angle2, elbow_angle2, target_x, target_y): 
    angle1a_deg = deg(shoulder_angle1) # shoulder angle a
    angle1b_deg = deg(shoulder_angle2) # shoulder angle b
    angle2a_deg = deg(elbow_angle1) # elbow angle a
    angle2b_deg = deg(elbow_angle2) # elbow angle b

    diff_a = abs(angle1a_deg) + abs(angle2a_deg) 
    diff_b = abs(angle1b_deg) + abs(angle2b_deg)

    if (diff_a <= diff_b):
        print(f"x={target_x}, y={target_y}: Solution 1 -> A1={shoulder_angle1} ({deg(shoulder_angle1)}°), A2={elbow_angle1} ({deg(elbow_angle1)}°)")
        return deg(shoulder_angle1), deg(elbow_angle1)
    else:
        print(f"x={target_x}, y={target_y}: Solution 2 -> A1={shoulder_angle2} ({deg(shoulder_angle2)}°), A2={elbow_angle2} ({deg(elbow_angle2)}°)")
        return deg(shoulder_angle2), deg(elbow_angle2)

def convert_angle_for_servo(angle):
    """Convert angle from -180 to 180 degrees to servo range 0 to 300 degrees."""
    if angle < 0:
        angle += 360
    return (angle / 360) * 300

# Provide a coordinate and calculate which angles the servos should (ideally) make.
def main(x, y):
    test_cases = [
        (x, y)
    ]

    for target_x, target_y in test_cases:
        try:
            (shoulder_angle1, elbow_angle1), (shoulder_angle2, elbow_angle2) = angles(target_x, target_y)
            angle1 = None
            angle2 = None
            blindSpot1 = blind_spot(shoulder_angle1, elbow_angle1)
            blindSpot2 = blind_spot(shoulder_angle2, elbow_angle2)
            if not blindSpot1 and not blindSpot2:
                angle1, angle2 = choice(shoulder_angle1, elbow_angle1, shoulder_angle2, elbow_angle2, target_x, target_y)
            elif not blindSpot1:
                print(f"x={target_x}, y={target_y}: Solution 1 -> A1={shoulder_angle1} ({deg(shoulder_angle1)}°), A2={elbow_angle1} ({deg(elbow_angle1)}°)")
                angle1 = deg(shoulder_angle1)
                angle2 = deg(elbow_angle1)
            else:
                print("Blind spot detected")
            
            if angle1 is not None and angle2 is not None:
                servo_angle1 = convert_angle_for_servo(angle1)
                servo_angle2 = convert_angle_for_servo(angle2)
                print(f"Servo Angle 1: {servo_angle1}°, Servo Angle 2: {servo_angle2}°")
                return servo_angle1, servo_angle2
        except ValueError as e:
            print(f"x={target_x}, y={target_y}: {e}")

if __name__ == "__main__":
    main(300, 300)
