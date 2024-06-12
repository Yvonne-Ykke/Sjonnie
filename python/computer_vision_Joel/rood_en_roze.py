import cv2
import numpy as np

def nothing(x):
    pass

def detect_pink(img, h_min, h_max, s_min, s_max, v_min, v_max):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for pink color in HSV
    lower_pink = np.array([h_min, s_min, v_min])
    upper_pink = np.array([h_max, s_max, v_max])

    # Create a mask using the inRange function
    mask = cv2.inRange(hsv, lower_pink, upper_pink)

    # Apply the mask to the original image
    result = cv2.bitwise_and(img, img, mask=mask)

    return result

# Open the camera
cap = cv2.VideoCapture(0)

cv2.namedWindow('image')

# Make trackbars for HSV ranges
cv2.createTrackbar('H_min', 'image', 0, 179, nothing)
cv2.createTrackbar('H_max', 'image', 179, 179, nothing)
cv2.createTrackbar('S_min', 'image', 0, 255, nothing)
cv2.createTrackbar('S_max', 'image', 255, 255, nothing)
cv2.createTrackbar('V_min', 'image', 0, 255, nothing)
cv2.createTrackbar('V_max', 'image', 255, 255, nothing)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if not ret:
        break

    # Read the current position of trackbars
    h_min = cv2.getTrackbarPos('H_min', 'image')
    h_max = cv2.getTrackbarPos('H_max', 'image')
    s_min = cv2.getTrackbarPos('S_min', 'image')
    s_max = cv2.getTrackbarPos('S_max', 'image')
    v_min = cv2.getTrackbarPos('V_min', 'image')
    v_max = cv2.getTrackbarPos('V_max', 'image')

    # Detect pink pixels and remove the masked area
    result = detect_pink(frame, h_min, h_max, s_min, s_max, v_min, v_max)

    # Display the result
    cv2.imshow('image', result)

    # Stop the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the camera and windows
cap.release()
cv2.destroyAllWindows()
