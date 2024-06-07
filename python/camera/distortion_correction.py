import numpy as np
import cv2 as cv
import os
from tkinter import Tk, Button

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
rows, cols = 8, 8
rows, cols = rows - 1, cols - 1
objp = np.zeros((rows * cols, 3), np.float32)
objp[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)
objpoints = []
imgpoints = []

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open camera")
    exit()

stop = False
screenshot_count = 0
screenshot_folder = 'screenshots'
os.makedirs(screenshot_folder, exist_ok=True)

def clear_screenshot_folder():
    for filename in os.listdir(screenshot_folder):
        file_path = os.path.join(screenshot_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def take_screenshot():
    global screenshot_count
    ret, frame = cap.read()
    if ret:
        screenshot_path = os.path.join(screenshot_folder, f'screenshot_{screenshot_count}.png')
        cv.imwrite(screenshot_path, frame)
        print(f'Screenshot {screenshot_count + 1} saved.')
        screenshot_count += 1
    if screenshot_count >= 10:
        stop_program()

def stop_program():
    global stop
    stop = True
    root.destroy()

# Clear screenshot folder at the beginning
clear_screenshot_folder()

# Set up the GUI
root = Tk()
root.title("Camera Calibration")
btn_screenshot = Button(root, text="Take Screenshot", command=take_screenshot)
btn_screenshot.pack()

# Main loop
while not stop:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (rows, cols), None)

    if ret:
        print("Chessboard corners found.")
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, ((rows * 2 + 1), (rows * 2 + 1)), (-1, -1), criteria)
        imgpoints.append(corners2)
        cv.drawChessboardCorners(frame, (rows, cols), corners2, ret)

    cv.imshow('frame', frame)
    if cv.waitKey(1) == 27:  # Escape key
        break

    root.update_idletasks()
    root.update()

cv.destroyAllWindows()
cap.release()

if not stop:
    if len(objpoints) > 0 and len(imgpoints) > 0:
        print("Calibrating camera...")
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        if ret:
            np.savez('calibration_data.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
            print("Camera calibration successful.")
            print("Camera matrix:\n", mtx)
            print("Distortion coefficients:\n", dist)
        else:
            print("Failed to calibrate camera")
    else:
        print("No calibration data collected.")
