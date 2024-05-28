import math

# Constants for the lengths of the robot's arm segments
LEN1 = 30.0
LEN2 = 30.0
# Current position of the servos
POS1 = 0 
POS2 = 0

def law_of_cosines(side1, side2, side3):
    """Calculate angle C using the law of cosines."""
    # Ensure side1 and side2 are not zero to prevent division by zero
    if side1 == 0 or side2 == 0:
        return 0
    try:
        return math.acos((side1 * side1 + side2 * side2 - side3 * side3) / (2 * side1 * side2))
    except ValueError:
        # Return NaN if the value inside acos is out of range due to floating-point precision issues
        return float('nan')

def distance(x, y):
    """Calculate the distance from the origin (0,0) to (x,y)."""
    return math.sqrt(x * x + y * y)

def angles(target_x, target_y):
    """Calculate the two sets of joint angles for given target_x and target_y."""
    dist = distance(target_x, target_y)
    
    if dist > (LEN1 + LEN2):
        raise ValueError("Target is out of reach")
    
    base_angle = math.atan2(target_y, target_x)
    elbow_angle = law_of_cosines(dist, LEN1, LEN2)
    
    # First set of angles
    shoulder_angle1 = base_angle + elbow_angle
    elbow_angle1 = law_of_cosines(LEN1, LEN2, dist)
    
    # Second set of angles (other solution)
    shoulder_angle2 = base_angle - elbow_angle
    elbow_angle2 = -elbow_angle1
    
    return (shoulder_angle1, elbow_angle1), (shoulder_angle2, elbow_angle2)

def deg(radians):
    """Convert radians to degrees."""
    return radians * 180 / math.pi

# Calculate the best angle, print it, and return it
def choice(shoulder_angle1, elbow_angle1, shoulder_angle2, elbow_angle2, current_pos1, current_pos2, target_x, target_y): 
    angle1a_deg = deg(shoulder_angle1) # shoulder angle a
    angle1b_deg = deg(shoulder_angle2) # shoulder angle b
    angle2a_deg = deg(elbow_angle1) # elbow angle a
    angle2b_deg = deg(elbow_angle2) # elbow angle b

    # Check if the shoulder and elbow do not have an angle they cannot make. If so, the object is unreachable
    if (-15 < angle2a_deg < 15 and -15 < angle2b_deg < 15 or -105 < angle1a_deg < -75 and -105 < angle1b_deg < -75):
        Exception(print("unreachable object detected"))
        return angle1a_deg, angle2a_deg
    # Check if only a has a valid angle and return b
    elif (-15 < angle2a_deg < 15 or -105 < angle1a_deg < -75): 
        print(f"x={target_x}, y={target_y}: Solution 2 -> A1={shoulder_angle2} ({deg(shoulder_angle2)}°), A2={elbow_angle2} ({deg(elbow_angle2)}°)")
        return deg(shoulder_angle2), deg(elbow_angle2)
    # Check if only b has a valid angle and return a
    elif (-15 < angle2b_deg < 15 or -105 < angle1b_deg < -75): 
        print(f"x={target_x}, y={target_y}: Solution 1 -> A1={shoulder_angle1} ({deg(shoulder_angle1)}°), A2={elbow_angle1} ({deg(elbow_angle1)}°)")
        return deg(shoulder_angle1), deg(elbow_angle1)
    # If no invalid angles are found
    else: 
       # Calculate the differences in angles and return the smallest angle as the best choice
       diff_a = abs(angle1a_deg) + abs(angle2a_deg) 
       diff_b = abs(angle1b_deg) + abs(angle2b_deg)

       if (diff_a <= diff_b):
            print(f"x={target_x}, y={target_y}: Solution 1 -> A1={shoulder_angle1} ({deg(shoulder_angle1)}°), A2={elbow_angle1} ({deg(elbow_angle1)}°)")
            return deg(shoulder_angle1), deg(elbow_angle1)
       else:
            print(f"x={target_x}, y={target_y}: Solution 2 -> A1={shoulder_angle2} ({deg(shoulder_angle2)}°), A2={elbow_angle2} ({deg(elbow_angle2)}°)")
            return deg(shoulder_angle2), deg(elbow_angle2)

# Provide a coordinate and calculate which angles the servos should (ideally) make.
def main():
    test_cases = [
        (25, 50)
    ]

    for target_x, target_y in test_cases:
        try:
            (shoulder_angle1, elbow_angle1), (shoulder_angle2, elbow_angle2) = angles(target_x, target_y)
            angle1, angle2 = choice(shoulder_angle1, elbow_angle1, shoulder_angle2, elbow_angle2, POS1, POS2, target_x, target_y)
            if (-105 < angle1 < -75 or -15 < angle2 < 15):
                Exception(print("unreachable object detected"))
            else:
                print(f"Angle 1 = {angle1}")
                print(f"Angle 2 = {angle2}")

        except ValueError as e:
            print(f"x={target_x}, y={target_y}: {e}")

if __name__ == "__main__":
    main()
