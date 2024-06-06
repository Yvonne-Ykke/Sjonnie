import numpy as np
import cv2 as cv

# Termination criteria for refining corner locations
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points for a 7x6 chessboard
objp = np.zeros((6*7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the frames
objpoints = []  # 3d points in real world space
imgpoints = []  # 2d points in image plane

# Capture video from the camera
cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)
    
    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)
        
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        
        # Draw and display the corners
        cv.drawChessboardCorners(frame, (7, 6), corners2, ret)
    
    # Display the frame
    cv.imshow('frame', frame)
    
    # Wait for a key press and break the loop if 'q' is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv.destroyAllWindows()

# Perform camera calibration
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save the camera calibration results for later use
np.savez('calibration_data.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

print("Camera matrix:\n", mtx)
print("Distortion coefficients:\n", dist)
