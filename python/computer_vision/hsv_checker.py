import cv2
import numpy as np

def get_hsv_values(frame, contour):
    # Create a mask for the current contour
    mask = np.zeros_like(frame)
    cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask the HSV frame using the mask of the contour
    masked_hsv = cv2.bitwise_and(hsv_frame, hsv_frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))

    # Get the HSV values within the contour
    hsv_values = cv2.mean(hsv_frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))[:3]
    return hsv_values

# Initialize the camera (0 is typically the default camera; change it if you have multiple cameras)
cap = cv2.VideoCapture(1)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Error: Cannot receive frame (stream end?). Exiting ...")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve contour detection
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply Canny edge detection
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and show HSV values
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            
            hsv_values = get_hsv_values(frame, contour)
            hsv_text = f"HSV: ({int(hsv_values[0])}, {int(hsv_values[1])}, {int(hsv_values[2])})"
            
            # Display the HSV values on the frame
            cv2.putText(frame, hsv_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('Result', frame)
    cv2.imshow('blurred', blurred)
    cv2.imshow('edged', edged)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
