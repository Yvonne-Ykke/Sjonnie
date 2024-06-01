import math

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
    angle_joint1_degrees -= 90
    
    return angle_joint1_degrees, angle_joint2_degrees

# Voorbeeldgebruik
target_x = 0
target_y = 600.0
arm_length1 = 300.0
arm_length2 = 300.0

angle_joint1_degrees, angle_joint2_degrees = inverse_kinematics(target_x, target_y, arm_length1, arm_length2)

print("Hoek gewricht 1:", angle_joint1_degrees, "graden")
print("Hoek gewricht 2:", angle_joint2_degrees, "graden")
