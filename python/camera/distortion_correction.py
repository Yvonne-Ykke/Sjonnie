import cv2
import numpy as np
import os

def calibrate_camera(objpoints, imgpoints, image_shape):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_shape[::-1], None, None)
    return ret, mtx, dist, rvecs, tvecs

def undistort_image(img, mtx, dist):
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # Correctie van de vervorming
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # Bijsnijden van het beeld
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    return dst

def image_to_world(image_point, rvec, tvec, mtx, dist):
    image_point = np.array([image_point], dtype=np.float32)
    image_point = np.expand_dims(image_point, axis=1)
    undistorted_point = cv2.undistortPoints(image_point, mtx, dist, P=mtx)
    undistorted_point = np.squeeze(undistorted_point)

    # Omzetten van beeldpunt naar 3D wereldcoördinaten
    world_point, _ = cv2.projectPoints(np.array([[0, 0, 0]]), rvec, tvec, mtx, dist)
    return world_point

def load_calibration_images(image_path):
    if not os.path.isfile(image_path):
        print(f"Error: Image file '{image_path}' does not exist.")
        return None, None

    objpoints = []  # 3D punten in de wereldruimte
    imgpoints = []  # 2D punten in de beeldruimte

    # Definieer het aantal hoeken in je checkerboard
    CHECKERBOARD = (6, 9)
    criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)

    # Voorbereiding van 3D punten in de wereldcoördinaten (0,0,0), (1,0,0), (2,0,0), ...
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Zoek de hoeken van het checkerboard
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

    return objpoints, imgpoints

# Voorbeeld gebruik
calibration_image = os.path.join('calibration_images', 'example.jpg')
objpoints, imgpoints = load_calibration_images(calibration_image)

if objpoints is not None and imgpoints is not None:
    gray_image = cv2.cvtColor(cv2.imread(calibration_image), cv2.COLOR_BGR2GRAY)
    image_shape = gray_image.shape

    ret, mtx, dist, rvecs, tvecs = calibrate_camera(objpoints, imgpoints, image_shape)

    example_image = cv2.imread(calibration_image)
    undistorted_image = undistort_image(example_image, mtx, dist)
    cv2.imwrite('calibrated_result.png', undistorted_image)

    # Voorbeeld van het omzetten van een beeldpunt naar een wereldcoördinaat
    image_point = [100, 200]  # Vervang door je eigen coördinaten
    rvec = rvecs[0]  # Rotatievector van de eerste afbeelding
    tvec = tvecs[0]  # Translatievector van de eerste afbeelding

    world_point = image_to_world(image_point, rvec, tvec, mtx, dist)
    print("World coordinates: ", world_point)

