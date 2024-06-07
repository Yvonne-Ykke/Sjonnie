import numpy as np
import cv2 as cv
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from movement import angle_calculator
# Load calibration data
calibration_data = np.load('calibration_data.npz')
mtx = calibration_data['mtx']
dist = calibration_data['dist']

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

# Undistort the frame
dst = cv.undistort(frame, mtx, dist, None, newcameramtx)

# Find chessboard corners
ret, corners = cv.findChessboardCorners(cv.cvtColor(dst, cv.COLOR_BGR2GRAY), (7, 7), None)

if ret:
    # Refine corner locations
    corners2 = cv.cornerSubPix(cv.cvtColor(dst, cv.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))

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

    # Draw the point on the image
    cv.circle(dst, (int(point_2d[0]), int(point_2d[1])), 5, (0, 0, 255), -1)
    cv.imshow('Projected Point', dst)
    cv.waitKey(0)
    cv.destroyAllWindows()
else:
    print("Chessboard corners not found")

# Given 3D point in world coordinates
point_3d = np.array([(10, 10, 10)], dtype=np.float32)  # Replace with actual coordinates

# Project to 2D image coordinates
point_2d, _ = cv.projectPoints(point_3d, rvec, tvec, mtx, dist)
point_2d = point_2d[0][0]
angle_calculator.main(point_2d[0], point_2d[1])


print("Projected point on image: ", point_2d)
