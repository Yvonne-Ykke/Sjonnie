import numpy as np
import cv2 as cv

# Load the calibration data
calibration_data = np.load('calibration_data.npz')
mtx = calibration_data['mtx']
dist = calibration_data['dist']

# Capture from the camera
cap = cv.VideoCapture(1)
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

# Live camera feed with undistortion
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Undistort the frame
    dst = cv.undistort(frame, mtx, dist, None, newcameramtx)

    # Crop the image (if necessary)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # Pad the undistorted image to match the original frame size
    if dst.shape[:2] != frame.shape[:2]:
        padded_dst = np.zeros_like(frame)
        padded_dst[:dst.shape[0], :dst.shape[1]] = dst
        dst = padded_dst

    # Stack the original and undistorted frames side by side
    combined = np.hstack((frame, dst))

    # Display the frames
    cv.imshow('Original and Undistorted Frames', combined)

    # Exit the loop on 'ESC' key press
    if cv.waitKey(1) == 27:  # ESC key
        break

# Release resources
cap.release()
cv.destroyAllWindows()
