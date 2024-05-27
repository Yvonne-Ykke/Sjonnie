import math

# Constants for the lengths of the robot's arm segments
LEN1 = 30.0
LEN2 = 30.0

def law_of_cosines(a, b, c):
    """Calculate angle C using the law of cosines."""
    # Ensure a and b are not zero to prevent division by zero
    if a == 0 or b == 0:
        return 0
    try:
        return math.acos((a*a + b*b - c*c) / (2 * a * b))
    except ValueError:
        # Return NaN if the value inside acos is out of range due to floating-point precision issues
        return float('nan')

def distance(x, y):
    """Calculate the distance from the origin (0,0) to (x,y)."""
    return math.sqrt(x*x + y*y)

def angles(x, y):
    """Calculate the two sets of joint angles for given x and y."""
    dist = distance(x, y)
    
    if dist > (LEN1 + LEN2):
        raise ValueError("Target is out of reach")
    
    D1 = math.atan2(y, x)
    D2 = law_of_cosines(dist, LEN1, LEN2)
    
    # First set of angles
    A1a = D1 + D2
    A2a = law_of_cosines(LEN1, LEN2, dist)
    
    # Second set of angles (other solution)
    A1b = D1 - D2
    A2b = -A2a
    
    return (A1a, A2a), (A1b, A2b)

def deg(rad):
    """Convert radians to degrees."""
    return rad * 180 / math.pi

def main():
    test_cases = [
        (40, 30),
        # (math.sqrt(LEN1*LEN1 + LEN2*LEN2), 0),
        # (1, 19),
        # (20, 0),
        # (0, 20),
        # (0, 0),
        # (20, 20)
    ]

    for x, y in test_cases:
        try:
            (a1a, a2a), (a1b, a2b) = angles(x, y)
            print(f"x={x}, y={y}: Solution 1 -> A1={a1a} ({deg(a1a)}°), A2={a2a} ({deg(a2a)}°)")
            print(f"x={x}, y={y}: Solution 2 -> A1={a1b} ({deg(a1b)}°), A2={a2b} ({deg(a2b)}°)")
        except ValueError as e:
            print(f"x={x}, y={y}: {e}")

if __name__ == "__main__":
    main()
