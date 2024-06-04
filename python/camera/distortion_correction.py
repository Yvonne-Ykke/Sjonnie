import cv2
import numpy as np
import glob

def calibrate_camera(calibration_images_path, checkerboard_size, square_size):
    # Termination criteria voor cornerSubPix
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Voorbereiden van objectpunten zoals (0,0,0), (1,0,0), (2,0,0), ...., (8,5,0)
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays opslaan objectpunten en beeldpunten van alle afbeeldingen
    objpoints = []  # 3d punten in de wereldruimte
    imgpoints = []  # 2d punten in afbeeldingsvlak

    # Laad kalibratieafbeeldingen
    images = glob.glob(calibration_images_path)

    if not images:
        raise ValueError("Geen kalibratieafbeeldingen gevonden.")

    gray = None
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Zoek de schaakbordhoeken
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

        # Als gevonden, verfijn hoekpunten en voeg toe aan de lijst
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Teken en toon de hoeken
            img = cv2.drawChessboardCorners(img, checkerboard_size, corners2, ret)
            cv2.imshow('img', img)

    cv2.destroyAllWindows()

    if gray is None:
        raise ValueError("Geen schaakbordhoeken gevonden in de kalibratieafbeeldingen.")

    # Kalibreer de camera
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return camera_matrix, dist_coeffs, rvecs, tvecs

def undistort_image(image_path, camera_matrix, dist_coeffs):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Gebruik undistort om de vervorming te corrigeren
    dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # Snijd de afbeelding bij
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]

    return dst

def pixel_to_world(pixel_point, depth, camera_matrix, rvec, tvec):
    # Inverse van de cameramatrix
    inv_camera_matrix = np.linalg.inv(camera_matrix)

    # Conversie naar homogene coördinaten
    pixel_homogeneous = np.array([pixel_point[0], pixel_point[1], 1.0])

    # Wereldcoördinaten berekenen
    world_point = np.dot(inv_camera_matrix, pixel_homogeneous) * depth
    world_point = np.dot(np.linalg.inv(cv2.Rodrigues(rvec)[0]), world_point - tvec)

    return world_point

# Configuraties
calibration_images_path = 'python\camera\calibration_images\*.jpg'  # Pad naar kalibratieafbeeldingen
example_image_path = 'python\camera\calibration_images\example.jpg'  # Pad naar een voorbeeldafbeelding om te undistorten
checkerboard_size = (9, 6)  # Aantal hoekpunten in de breedte en hoogte
square_size = 1.0  # Grootte van een vierkant op het schaakbord, in dezelfde eenheden als je wereldcoördinaten

# Camera kalibratie
camera_matrix, dist_coeffs, rvecs, tvecs = calibrate_camera(calibration_images_path, checkerboard_size, square_size)
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)

# Afbeelding undistorten
undistorted_image = undistort_image(example_image_path, camera_matrix, dist_coeffs)
cv2.imshow('Undistorted Image', undistorted_image)

cv2.waitKey(0)
cv2.destroyAllWindows()

# Pixel naar wereldcoördinaten omzetting
pixel_point = (100, 150)  # Pixelcoördinaten
depth = 2.0  # Diepte of hoogte op basis waarvan je de wereldcoördinaten wilt bepalen

# Neem de eerste rotatie- en translatievector van de kalibratie
rvec = rvecs[0]
tvec = tvecs[0]

world_point = pixel_to_world(pixel_point, depth, camera_matrix, rvec, tvec)
print("World coordinates:", world_point)
