import matplotlib.pyplot as plt
import numpy as np

# Parameters
ARM_1_LENGHT = 300  # Lengte eerste as
ARM_2_LENGHT = 300  # Lengte tweede as

# Hoeken van -150 tot 150 graden voor beide assen
shoulder_angles = np.radians(np.linspace(-150, 150, 300))
elbow_angles = np.radians(np.linspace(-150, 150, 300))

reachable_coordinates = []

for shoulder_angle in shoulder_angles:
    for elbow_angle in elbow_angles:
        x = ARM_1_LENGHT * np.cos(shoulder_angle) + ARM_2_LENGHT * np.cos(shoulder_angle + elbow_angle)
        y = ARM_1_LENGHT * np.sin(shoulder_angle) + ARM_2_LENGHT * np.sin(shoulder_angle + elbow_angle)
        
        # Voeg alleen bereikbare coördinaten toe (vermijd de dode hoeken)
        if -150 <= np.degrees(shoulder_angle) <= 150 and -150 <= np.degrees(elbow_angle) <= 150:
            reachable_coordinates.append((x, y))

# Haal de x- en y-coördinaten uit de lijst van tuples
x_reach, y_reach = zip(*reachable_coordinates)

# Plot bereikbare coördinaten met omgekeerde assen
def plot():
    plt.figure(figsize=(8, 8))
    plt.plot(y_reach, x_reach, 'b.', markersize=1, label="Bereikbare Coördinaten")
    plt.xlabel("y (mm)")
    plt.ylabel("x (mm)")
    plt.title("Bereikbare Coördinaten van de Robotarm (Omgekeerde Assen)")
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.axis('equal')
    plt.show()

def checkBlindSpot():
    test_cases = [
        (250, 500),
        (0,0),
        (700,0),
        (100,20),
        (200,400)
    ]

    for x, y in test_cases:
            # Bereken de afstand van de oorsprong (0,0) naar (x,y)
            dist = np.sqrt(x * x + y * y)

            # Bereken de twee sets van gewrichtshoeken voor gegeven target_x en target_y
            if dist > (ARM_1_LENGHT + ARM_2_LENGHT):
                print("Doel is onbereikbaar" + " x: " + str(x) + ", y: " + str(y))
            else:
                base_angle = np.arctan2(y, x)
                elbow_angle = np.arccos((x**2 + y**2 - ARM_1_LENGHT**2 - ARM_2_LENGHT**2) / (2 * ARM_1_LENGHT * ARM_2_LENGHT))

                # Eerste set hoeken
                shoulder_angle = base_angle + elbow_angle
                elbow_angle = np.arccos((ARM_1_LENGHT**2 + ARM_2_LENGHT**2 - x**2 - y**2) / (2 * ARM_1_LENGHT * ARM_2_LENGHT))

                # Converteer radialen naar graden
                shoulder_angle_in_deg = np.degrees(shoulder_angle)
                elbow_angle_in_deg = np.degrees(elbow_angle)

    # Controleer of de schouder en elleboog geen hoek hebben die ze niet kunnen maken. Zo ja, is het object onbereikbaar
    
                if (-30 < elbow_angle_in_deg < 30 or -120 < shoulder_angle_in_deg < -60):
                    print("Blindspot gevonden" + " x: " + str(x) + ", y: " + str(y))   
                else:
                    print("geen blindspot gevonden" + " x: " + str(x) + ", y: " + str(y))

plot()
checkBlindSpot()
