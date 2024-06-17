import numpy as np
import cv2 as cv

# Load the calibration data
calibration_data = np.load('calibration_data.npz')
mtx = calibration_data['mtx']
dist = calibration_data['dist']

# Chessboard parameters
square_size_mm = 19.5
pattern_size = (7, 7)  # Inner corners per a chessboard row and column

# Capture from the camera
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open camera")
    exit()

# Get frame dimensions
ret, frame = cap.read()
if not ret:
    print("Failed to capture image")
    cap.release()
    exit()

h, w = frame.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# Variables for storing pixel distances and scale factors
pixel_distances = []
scale_factors = []

# Loop to check the chessboard 10 times
for _ in range(100):
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Undistort the frame
    dst = cv.undistort(frame, mtx, dist, None, newcameramtx)

    # Convert to grayscale
    gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, pattern_size, None)

    if ret:
        # Refine the corner locations
        corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        # Calculate the pixel distance between the first two adjacent corners
        pixel_distance = np.linalg.norm(corners[0] - corners[1])

        # Calculate the scale factor (mm per pixel)
        scale_factor = square_size_mm / pixel_distance
        
        # Store pixel distance and scale factor
        pixel_distances.append(pixel_distance)
        scale_factors.append(scale_factor)

    # Draw the corners
    cv.drawChessboardCorners(frame, pattern_size, corners, ret)

    # Display the frames
    cv.imshow('Chessboard and Undistorted Frame', frame)
    cv.waitKey(10)
    # Exit the loop on 'ESC' key press
    if cv.waitKey(1) == 27:  # ESC key
        break

# Release resources
cap.release()
cv.destroyAllWindows()

# Calculate the average pixel distance and scale factor
average_pixel_distance = np.mean(pixel_distances)
average_scale_factor = np.mean(scale_factors)

print(f"Average pixel distance between adjacent corners: {average_pixel_distance:.2f} pixels")
print(f"Average scale factor: {average_scale_factor:.6f} mm per pixel")
