import math

# Constants for the lengths of the robot's arm segments
LEN1 = 30.0
LEN2 = 30.0
#Current position of the servo's
POS1 = 0 
POS2 = 0

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

#Berekent beste hoek, print deze en geeft hem terug
def choice(a1a, a2a, a1b, a2b, pos1, pos2, x ,y): 
    angle1a = deg(a1a) #schouder hoek a
    angle1b = deg(a1b) #schouder hoek b
    angle2a = deg(a2a) #elleboog hoek a
    angle2b = deg(a2b) #elleboog hoek b

#Check of de schouder en elleboog geen hoek hebben die ze niet kunnen maken. Als dat wel zo is dan is het object unreachable
    if(-15 < angle2a < 15 and -15 < angle2b < 15 or -105 < angle1a < -75 and -105 < angle1b < -75):
        Exception(print("unreachable object detected"))
        return angle1a, angle2a
    #check of alleen a een doede hoek heeft en return b
    elif(-15 < angle2a < 15 or -105 < angle1a < -75): 
        print(f"x={x}, y={y}: Solution 2 -> A1={a1b} ({deg(a1b)}°), A2={a2b} ({deg(a2b)}°)")
        return deg(a1b), deg(a2b)
    #check of alleen b een doede hoek heeft en return a
    elif(-15 < angle2b < 15 or -105 < angle1b < -75): 
        print(f"x={x}, y={y}: Solution 1 -> A1={a1a} ({deg(a1a)}°), A2={a2a} ({deg(a2a)}°)")
        return deg(a1a), deg(a2a)
    #als er geen dode hoeken gevonden zijn
    else: 
       #bereken de verschillen in hoeken en geef de kleinste hoek terug als beste keuze
       difa = abs(angle1a) + abs(angle2a) 
       difb = abs(angle1b) + abs(angle2b)

       if(difa <= difb):
            print(f"x={x}, y={y}: Solution 1 -> A1={a1a} ({deg(a1a)}°), A2={a2a} ({deg(a2a)}°)")
            return deg(a1a), deg(a2a)
       else:
            print(f"x={x}, y={y}: Solution 2 -> A1={a1b} ({deg(a1b)}°), A2={a2b} ({deg(a2b)}°)")
            return deg(a1b), deg(a2b)

#Geef een coördinaat mee en bereken welke hoeken de servo's (het best) moeten maken.
def main():
    test_cases = [
        (25, 50)
    ]

    for x, y in test_cases:
        try:
            (a1a, a2a), (a1b, a2b) = angles(x, y)
            angle1, angle2 = choice(a1a, a2a, a1b, a2b, POS1, POS2, x , y)
            if(-105 < angle1 < -75 or -15 < angle2 < 15):
                Exception(print("unreachable object detected"))
            else:
                print(f"Angle 1 = {angle1}")
                print(f"Angle 2 = {angle2}")

        except ValueError as e:
            print(f"x={x}, y={y}: {e}")
            

if __name__ == "__main__":
    main()
