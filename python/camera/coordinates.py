import numpy as np
import cv2 as cv
import sys
import os

# Import angle_calculator function from movement module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from movement import angle_calculator

# Load calibration data
calibration_data = np.load('calibration_data.npz')
mtx = calibration_data['mtx']
dist = calibration_data['dist']

# Assuming these values are known
camera_origin_x, camera_origin_y = 0, 0  # Camera origin in its coordinate system
scale_factor = 1  # 1 unit in camera coordinates = 1 mm

# Function to transform coordinates
def transform_coordinates(camera_x, camera_y):
    # Translate coordinates so that the shoulder servo is at (0,0)
    translated_x = camera_x - camera_origin_x
    translated_y = camera_y - camera_origin_y
    
    # Scale the coordinates
    robot_x = translated_x * scale_factor
    robot_y = translated_y * scale_factor
    
    return robot_x, robot_y

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

h, w = frame.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# Live camera feed with undistortion and chessboard detection

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Undistort the frame
    dst = cv.undistort(frame, mtx, dist, None, newcameramtx)

    # Convert to grayscale
    gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, (7, 7), None)

    if ret:
        # Refine the corner locations
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        # Draw and display the corners
        cv.drawChessboardCorners(dst, (7, 7), corners2, ret)
        cv.imshow('Chessboard', dst)
        cv.waitKey(500)

        # Assuming the chessboard is at z=0 (flat on a table)
        objp = np.zeros((7*7, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

        # Find the rotation and translation vectors
        ret, rvec, tvec = cv.solvePnP(objp, corners2, mtx, dist)

        # Project a point in 3D space (e.g., (3, 3, 0)) to image coordinates
        point_3d = np.array([(3, 3, 0)], dtype=np.float32)  # A point on the chessboard
        point_2d, _ = cv.projectPoints(point_3d, rvec, tvec, mtx, dist)
        point_2d = point_2d[0][0]

        print("Projected point on image: ", point_2d)

        # Transform camera coordinates to robot coordinates
        robot_x, robot_y = transform_coordinates(point_2d[0], point_2d[1])
        print("Robot coordinates: ", (robot_x, robot_y))

        # Draw the point on the image
        cv.circle(dst, (int(point_2d[0]), int(point_2d[1])), 5, (0, 0, 255), -1)
        cv.imshow('Projected Point', dst)
        cv.waitKey(0)
        cv.destroyAllWindows()
        angle_calculator.main(robot_x, robot_y)
        break
    else:
        print("Chessboard corners not found")

    # Exit the loop on 'ESC' key press
    if cv.waitKey(1) == 27:  # ESC key
        break

# Release resources
cap.release()
cv.destroyAllWindows()
