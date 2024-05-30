import matplotlib.pyplot as plt
import numpy as np

# Parameters
L1 = 300  # Lengte eerste as
L2 = 300  # Lengte tweede as

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
            if dist > (L1 + L2):
                print("Doel is onbereikbaar" + " x: " + str(x) + ", y: " + str(y))
            else:
                basis_hoek = np.arctan2(y, x)
                elleboog_hoek = np.arccos((x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2))

                # Eerste set hoeken
                schouder_hoek1 = basis_hoek + elleboog_hoek
                elleboog_hoek1 = np.arccos((L1**2 + L2**2 - x**2 - y**2) / (2 * L1 * L2))

                # Tweede set hoeken (andere oplossing)
                schouder_hoek2 = basis_hoek - elleboog_hoek
                elleboog_hoek2 = -elleboog_hoek1

                # Converteer radialen naar graden
                schouder_hoek1_deg = np.degrees(schouder_hoek1)
                elleboog_hoek1_deg = np.degrees(elleboog_hoek1)
                schouder_hoek2_deg = np.degrees(schouder_hoek2)
                elleboog_hoek2_deg = np.degrees(elleboog_hoek2)

    # Controleer of de schouder en elleboog geen hoek hebben die ze niet kunnen maken. Zo ja, is het object onbereikbaar
    
                if (-30 < elleboog_hoek1_deg < 30 or -120 < schouder_hoek1_deg < -60):
                    print("Blindspot gevonden" + " x: " + str(x) + ", y: " + str(y))   
                else:
                    print("geen blindspot gevonden" + " x: " + str(x) + ", y: " + str(y))

plot()
checkBlindSpot()
