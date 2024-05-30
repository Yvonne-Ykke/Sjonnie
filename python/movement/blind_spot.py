import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

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
            reachable_coordinates.append([x, y])

# Converteer naar numpy array voor gebruik met ConvexHull
reachable_coordinates = np.array(reachable_coordinates)

# Bereken de convex hull
hull = ConvexHull(reachable_coordinates)

# Plot bereikbare coördinaten met omgekeerde assen
def plot():
    plt.figure(figsize=(8, 8))
    plt.plot(reachable_coordinates[:, 0], reachable_coordinates[:, 1], 'b.', markersize=1, label="Bereikbare Coördinaten")
    
    # Plot de convex hull
    for simplex in hull.simplices:
        plt.plot(reachable_coordinates[simplex, 0], reachable_coordinates[simplex, 1], 'r-')

    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    plt.title("Bereikbare Coördinaten van de Robotarm met Convex Hull")
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.axis('equal')
    plt.show()

plot()
