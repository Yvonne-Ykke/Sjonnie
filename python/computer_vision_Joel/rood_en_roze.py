import cv2
import numpy as np

# Global variables to store clicked points
points = []

def nothing(x):
    pass

def detect_red(img, h_low1, h_high1, s_low1, s_high1, v_low1, v_high1,
               h_low2, h_high2, s_low2, s_high2, v_low2, v_high2):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for red color in HSV (1st range)
    lower_red1 = np.array([h_low1, s_low1, v_low1])
    upper_red1 = np.array([h_high1, s_high1, v_high1])

    # Define lower and upper bounds for red color in HSV (2nd range)
    lower_red2 = np.array([h_low2, s_low2, v_low2])
    upper_red2 = np.array([h_high2, s_high2, v_high2])

    # Create masks using the inRange function for both ranges
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine the masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Apply the mask to the original image
    result = cv2.bitwise_and(img, img, mask=mask)

    return result

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

# Open the camera
cap = cv2.VideoCapture(0)

cv2.namedWindow('image')
cv2.setMouseCallback('image', mouse_callback)

# Make trackbars for HSV ranges
cv2.createTrackbar('H_low1', 'image', 0, 179, nothing)
cv2.createTrackbar('H_high1', 'image', 10, 179, nothing)
cv2.createTrackbar('S_low1', 'image', 100, 255, nothing)
cv2.createTrackbar('S_high1', 'image', 255, 255, nothing)
cv2.createTrackbar('V_low1', 'image', 100, 255, nothing)
cv2.createTrackbar('V_high1', 'image', 255, 255, nothing)

cv2.createTrackbar('H_low2', 'image', 160, 179, nothing)
cv2.createTrackbar('H_high2', 'image', 179, 179, nothing)
cv2.createTrackbar('S_low2', 'image', 100, 255, nothing)
cv2.createTrackbar('S_high2', 'image', 255, 255, nothing)
cv2.createTrackbar('V_low2', 'image', 100, 255, nothing)
cv2.createTrackbar('V_high2', 'image', 255, 255, nothing)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if not ret:
        break

    # Read the current position of trackbars for both ranges
    h_low1 = cv2.getTrackbarPos('H_low1', 'image')
    h_high1 = cv2.getTrackbarPos('H_high1', 'image')
    s_low1 = cv2.getTrackbarPos('S_low1', 'image')
    s_high1 = cv2.getTrackbarPos('S_high1', 'image')
    v_low1 = cv2.getTrackbarPos('V_low1', 'image')
    v_high1 = cv2.getTrackbarPos('V_high1', 'image')

    h_low2 = cv2.getTrackbarPos('H_low2', 'image')
    h_high2 = cv2.getTrackbarPos('H_high2', 'image')
    s_low2 = cv2.getTrackbarPos('S_low2', 'image')
    s_high2 = cv2.getTrackbarPos('S_high2', 'image')
    v_low2 = cv2.getTrackbarPos('V_low2', 'image')
    v_high2 = cv2.getTrackbarPos('V_high2', 'image')

    # Detect red pixels and remove the masked area
    result = detect_red(frame, h_low1, h_high1, s_low1, s_high1, v_low1, v_high1,
                        h_low2, h_high2, s_low2, s_high2, v_low2, v_high2)

    # Draw circles on the clicked points
    for point in points:
        cv2.circle(result, point, 5, (0, 255, 0), -1)

    # Display the result
    cv2.imshow('image', result)

    # Stop the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the camera and windows
cap.release()
cv2.destroyAllWindows()
ZZ