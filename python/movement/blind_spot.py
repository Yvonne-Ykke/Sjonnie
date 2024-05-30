import matplotlib.pyplot as plt
import numpy as np

# Parameters
L1 = 30  # Lengte eerste as
L2 = 30  # Lengte tweede as

# Hoeken van -150 tot 150 graden voor beide assen
theta1 = np.radians(np.linspace(-150, 150, 300))
theta2 = np.radians(np.linspace(-150, 150, 300))

# Bereken de bereikbare coördinaten
y_reach = []
x_reach = []

for t1 in theta1:
    for t2 in theta2:
        x = L1 * np.cos(t1) + L2 * np.cos(t1 + t2)
        y = L1 * np.sin(t1) + L2 * np.sin(t1 + t2)
        # Voeg alleen bereikbare coördinaten toe (vermijd de dode hoeken)
        if -150 <= np.degrees(t1) <= 150 and -150 <= np.degrees(t2) <= 150:
            x_reach.append(x)
            y_reach.append(y)

# Plot bereikbare coördinaten met omgekeerde assen
plt.figure(figsize=(8, 8))
plt.plot(y_reach, x_reach, 'b.', markersize=1, label="Bereikbare Coördinaten")
plt.xlabel("y (cm)")
plt.ylabel("x (cm)")
plt.title("Bereikbare Coördinaten van de Robotarm (Omgekeerde Assen)")
plt.grid(True)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.legend()
plt.axis('equal')
plt.show()
