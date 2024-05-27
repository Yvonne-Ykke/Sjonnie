import math

# Constants for the lengths of the robot's arm segments
LEN1 = 10.0
LEN2 = 10.0

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
    """Calculate the two joint angles for given x and y."""
    dist = distance(x, y)
    D1 = math.atan2(y, x)
    D2 = law_of_cosines(dist, LEN1, LEN2)
    A1 = D1 + D2
    A2 = law_of_cosines(LEN1, LEN2, dist)
    return A1, A2

def deg(rad):
    """Convert radians to degrees."""
    return rad * 180 / math.pi

def main():
    test_cases = [
        (5, 5),
        (math.sqrt(200), 0),
        (1, 19),
        (20, 0),
        (0, 20),
        (0, 0),
        (20, 20)
    ]

    for x, y in test_cases:
        a1, a2 = angles(x, y)
        print(f"x={x}, y={y}: A1={a1} ({deg(a1)}°), A2={a2} ({deg(a2)}°)")

if __name__ == "__main__":
    main()
