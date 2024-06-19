import cv2
import numpy as np

# Functie om centroids van geschikte contouren te vinden en te tekenen
def find_and_draw_centroids(frame):
    # Converteer het frame naar grijswaarden
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Binarizeer het frame door een drempel toe te passen
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Vind contouren in de binarized frame
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Loop over de contouren
    for contour in contours:
        # Bereken de oppervlakte van het contour
        area = cv2.contourArea(contour)
        
        # Bereken de omtrek van het contour
        perimeter = cv2.arcLength(contour, True)
        
        # Bereken de rondheidsfactor
        if perimeter > 0:
            roundness = (4 * np.pi * area) / (perimeter * perimeter)
        else:
            roundness = 0
        
        # Controleer of het contour enige rondheid heeft en een minimale grootte van 500 pixels heeft
        if area > 50 and roundness > 0.4:  # Aanpassen van de roundness-threshold naar wens
            # Bereken de momenten van het contour
            M = cv2.moments(contour)
            
            # Bereken de centroid (cx, cy)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0
            
            # Teken een cirkel op het frame op de positie van de centroid
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)  # Hier (255, 0, 0) is de kleur in BGR formaat
    
    return frame

# Hoofdcode om de webcam te openen en geschikte contouren te detecteren
cap = cv2.VideoCapture(0)  # Open de webcam (meestal 0 voor de ingebouwde webcam)

while True:
    ret, frame = cap.read()  # Lees een frame van de webcam
    
    if not ret:
        break
    
    # Roep de functie aan om centroids van geschikte contouren te vinden en te tekenen
    frame_with_centroids = find_and_draw_centroids(frame)
    
    # Toon het frame met de getekende centroids
    cv2.imshow('Frame with Centroids', frame_with_centroids)
    
    # Stop de loop als 'q' wordt ingedrukt
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Sluit de webcam en vensters
cap.release()
cv2.destroyAllWindows()
