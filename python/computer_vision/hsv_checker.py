import cv2
import numpy as np

def get_hsv_range(frame, contour):
    # Create a mask for the current contour
    mask = np.zeros_like(frame)
    cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask the HSV frame using the mask of the contour
    masked_hsv = cv2.bitwise_and(hsv_frame, hsv_frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))

    # Extract the HSV values within the contour
    hsv_values = masked_hsv[np.where(mask[:, :, 0] == 255)]
    
    if hsv_values.size == 0:
        return (0, 0, 0), (0, 0, 0)
    
    # Get the minimum and maximum HSV values
    min_hsv = np.min(hsv_values, axis=0)
    max_hsv = np.max(hsv_values, axis=0)

    return min_hsv, max_hsv

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
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and show HSV values
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            
            min_hsv, max_hsv = get_hsv_range(frame, contour)
            hsv_text = f"Min HSV: ({int(min_hsv[0])}, {int(min_hsv[1])}, {int(min_hsv[2])}) Max HSV: ({int(max_hsv[0])}, {int(max_hsv[1])}, {int(max_hsv[2])})"
            
            # Display the HSV values on the frame
            cv2.putText(frame, hsv_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('Result', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
