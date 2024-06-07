import numpy as np
import cv2 as cv

# Chessboard parameters
square_size_mm = 19.5
pattern_size = (7, 7)  # Inner corners per a chessboard row and column

# Capture from the camera
cap = cv.VideoCapture(1)
if not cap.isOpened():
    print("Failed to open camera")
    exit()

ret, frame = cap.read()
if not ret:
    print("Failed to capture image")
    cap.release()
    exit()

# Convert to grayscale
gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

# Find the chessboard corners
ret, corners = cv.findChessboardCorners(gray, pattern_size, None)

if ret:
    # Refine the corner locations
    corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))

    # Draw the corners
    cv.drawChessboardCorners(frame, pattern_size, corners, ret)
    cv.imshow('Chessboard', frame)
    cv.waitKey(0)

    # Calculate the pixel distance between the first two adjacent corners
    pixel_distance = np.linalg.norm(corners[0] - corners[1])

    # Calculate the scale factor (mm per pixel)
    scale_factor = square_size_mm / pixel_distance
    print(f"Pixel distance between adjacent corners: {pixel_distance:.2f} pixels")
    print(f"Scale factor: {scale_factor:.6f} mm per pixel")

else:
    print("Chessboard corners not found")

cv.destroyAllWindows()
cap.release()
