import numpy as np
import matplotlib.pyplot as plt

# Parameters
ARM_1_LENGTH = 300  # Lengte van de eerste armsegment
ARM_2_LENGTH = 300  # Lengte van de tweede armsegment

# Hoeken van -150 tot 150 graden voor beide armsegmenten, geconverteerd naar radialen
shoulder_angles = np.radians(np.linspace(-150, 150, 300))
elbow_angles = np.radians(np.linspace(-150, 150, 300))

reachable_coordinates = []

for shoulder_angle in shoulder_angles:
    for elbow_angle in elbow_angles:
        x = ARM_1_LENGTH * np.cos(shoulder_angle) + ARM_2_LENGTH * np.cos(shoulder_angle + elbow_angle)
        y = ARM_1_LENGTH * np.sin(shoulder_angle) + ARM_2_LENGTH * np.sin(shoulder_angle + elbow_angle)
        
        # Voeg alleen bereikbare coördinaten toe (vermijd de dode hoeken)
        if -150 <= np.degrees(shoulder_angle) <= 150 and -150 <= np.degrees(elbow_angle) <= 150:
            reachable_coordinates.append((x, y))

# Haal de x- en y-coördinaten uit de lijst van tuples
x_reach, y_reach = zip(*reachable_coordinates)

# Functie om te controleren of een locatie bereikbaar is
def check_reachability(x, y):
    # Bereken de afstand van de oorsprong (0, 0) naar (x, y)
    dist = np.sqrt(x * x + y * y)

    # Controleer of de doelcoördinaat binnen het bereik van de arm valt
    if dist > (ARM_1_LENGTH + ARM_2_LENGTH):
        print(f"Doel is onbereikbaar: x={x}, y={y}")
        return False
    else:
        base_angle = np.arctan2(y, x)
        elbow_angle = np.arccos((x**2 + y**2 - ARM_1_LENGTH**2 - ARM_2_LENGTH**2) / (2 * ARM_1_LENGTH * ARM_2_LENGTH))

        # Eerste set hoeken
        shoulder_angle = base_angle + elbow_angle
        elbow_angle = np.arccos((ARM_1_LENGTH**2 + ARM_2_LENGTH**2 - x**2 - y**2) / (2 * ARM_1_LENGTH * ARM_2_LENGTH))

        # Converteer radialen naar graden
        shoulder_angle_in_deg = np.degrees(shoulder_angle)
        elbow_angle_in_deg = np.degrees(elbow_angle)

        # Controleer of de schouder en elleboog geen hoek hebben die ze niet kunnen maken. Zo ja, is het object onbereikbaar
        if (-30 < elbow_angle_in_deg < 30 or -120 < shoulder_angle_in_deg < -60):
            print(f"Blindspot gevonden: x={x}, y={y}")
            return False
        else:
            print(f"Geen blindspot gevonden: x={x}, y={y}")
            return True

# Event handler voor muisklikken
def on_click(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        print(f"Klik op: x={x}, y={y}")
        check_reachability(x, y)

# Plot bereikbare coördinaten met omgekeerde assen
def plot():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(y_reach, x_reach, 'b.', markersize=1, label="Bereikbare Coördinaten")
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("x (mm)")
    ax.set_title("Bereikbare Coördinaten van de Robotarm (Omgekeerde Assen)")
    ax.grid(True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.legend()
    ax.axis('equal')

    # Verbind de klik event handler aan de plot
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()

plot()
