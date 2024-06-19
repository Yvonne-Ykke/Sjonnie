import numpy as np
import cv2 as cv
import sys
import os
import time
from sklearn.linear_model import LinearRegression
from coordinate_transformation import CoordinateTransformer
import wrist_rotation

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importeer bewegingsmodules
import movement.robot_arm_parameters as robot_arm_parameters
import movement.angle_calculator as angle_calculator
import movement.client as client

import computer_vision.color_recognition as color_definitions

conversion_rate = 1.1398

# Callbackfunctie voor trackbars
def nothing(x):
    pass

# Maak trackbars
def create_trackbars():
    cv.namedWindow('settings')
    cv.createTrackbar('Min Area', 'settings', 1000, 2000, nothing)
    cv.createTrackbar('Max Area', 'settings', 1500, 5000, nothing)

# Haal waarden op van de trackbars
def get_trackbar_values():
    min_area = cv.getTrackbarPos('Min Area', 'settings')
    max_area = cv.getTrackbarPos('Max Area', 'settings')
    return min_area, max_area

# Klikgebeurtenis
def click_event(event, x, y, flags, params):
    if event == cv.EVENT_LBUTTONDOWN:
        real_world_coords = params.convert_coordinates([(x, y)])
        print(f"Clicked Coordinates: ({x}, {y}) -> Real World Coordinates: {real_world_coords}")
        
        # Haal x en y op van het eerste element van real_world_coords
        real_world_x, real_world_y = real_world_coords[0]
        shoulder, elbow = angle_calculator.main(real_world_x, real_world_y)

        if shoulder is not None and elbow is not None:
            client.send_arm_angles_to_robot(shoulder, -elbow, 45)
            print(f"Shoulder: {shoulder}, Elbow: {elbow}")
        else:
            print("Unable to calculate shoulder or elbow angle.")

# Voorspel traject
def predict_trajectory(positions):
    if len(positions) < 2:
        return None, None

    times = np.array([pos[0] for pos in positions]).reshape(-1, 1)
    x_coords = np.array([pos[1] for pos in positions])
    y_coords = np.array([pos[2] for pos in positions])

    x_model = LinearRegression().fit(times, x_coords)
    y_model = LinearRegression().fit(times, y_coords)

    return x_model, y_model

# Kleurcontouren
def color_contouring(developing, transformer, color_name_to_track):
    cap = cv.VideoCapture(0)
    create_trackbars()

    cv.namedWindow('image')
    cv.setMouseCallback('image', click_event, param=transformer)

    tracked_positions = []

    while True:
        ret, img = cap.read()
        if img is None:
            break

        # Undistort the captured frame
        img = cv.undistort(img, transformer.mtx, transformer.dist)

        # Haal kleurmaskers op
        color_masks = color_definitions.masks(img)

        for color_name, mask, bgr in color_masks:
            if color_name == color_name_to_track:  # Alleen de gewenste kleur volgen
                res = cv.bitwise_and(img, img, mask=mask)
                imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
                blur = cv.GaussianBlur(imgray, (3, 3), 0)
                ret, threshoog = cv.threshold(imgray, 1, 255, cv.THRESH_BINARY)
                contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

                if hierarchy is not None:
                    hierarchy = hierarchy[0]

                min_area, max_area = get_trackbar_values()

                for cnt in contours:
                    area = cv.contourArea(cnt)
                    if min_area < area < max_area:                   
                        M = cv.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            real_world_coords = transformer.convert_coordinates([(cX, cY)])
                            real_world_x, real_world_y = real_world_coords[0]
                            current_time = time.time()
                            tracked_positions.append((current_time, real_world_x, real_world_y))

                            if len(tracked_positions) > 100:
                                tracked_positions.pop(0)

                            # Haal het minimumomtrekrect op
                            rect = cv.minAreaRect(cnt)
                            box = cv.boxPoints(rect)
                            box = np.int0(box)
                            objectAngle = rect[2]
                            width, height = rect[1]
                            if width < height:
                                objectAngle = objectAngle + 90  # Pas de hoek aan

                            # Teken het contour, zwaartepunt en hoek
                            cv.drawContours(img, [cnt], -1, (0, 255, 0), 3)  # Teken contour in groen
                            cv.circle(img, (cX, cY), 5, (0, 0, 255), -1)  # Teken zwaartepunt in rood
                            cv.drawContours(img, [box], 0, (255, 0, 0), 2)  # Teken rechthoek in blauw
                            cv.putText(img, f"{real_world_coords[0][0]:.2f}, {real_world_coords[0][1]:.2f}", (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                            cv.putText(img, f"Angle: {objectAngle:.2f}", (cX + 50, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)

                            if len(tracked_positions) > 1:
                                x_model, y_model = predict_trajectory(tracked_positions)
                                if x_model is not None and y_model is not None:
                                    future_time = current_time + 1  # Voorspel 1 seconde in de toekomst
                                    future_x = x_model.predict(np.array([[future_time]]))[0]
                                    future_y = y_model.predict(np.array([[future_time]]))[0]
                                    shoulder, elbow = angle_calculator.main(future_x, future_y)
                                    if elbow is not None:
                                        wrist_angle = wrist_rotation.calculate_wrist_rotation(shoulder, -elbow, objectAngle)
                                        # client.send_arm_angles_to_robot(shoulder, -elbow, wrist_angle)  # Stuur hoeken naar robotarm
                                        print(f"Predicted - Shoulder: {shoulder}, Elbow: {elbow}, Wrist: {wrist_angle}")

                                        # Teken het voorspelde traject op de afbeelding
                                        cv.line(img, (int(future_x), int(future_y)), (int(future_x), int(future_y)), (0, 0, 255), 2)

        if developing:
            cv.imshow("image", img)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

if __name__ == "__main__":
    # Definieer cameracoördinaten (x, y) en bijbehorende werkelijke wereldcoördinaten (X, Y)
    camera_coords = [
        [313, 223],
        [313, 293],
        [313, 363],
        [374, 223],
        [374, 293],
        [374, 363],
        [434, 223],
        [434, 293],
        [434, 362]
    ]

    real_world_coords = [
        [-140, 375],
        [-140, 295],
        [-140, 215],
        [-70, 374],
        [-70, 294],
        [-70, 214],
        [0, 375],
        [0, 298],
        [0, 219]
    ]

    # Initialiseren van de transformer met de conversiesnelheid
    transformer = CoordinateTransformer(camera_coords, real_world_coords, conversion_rate)

    # Track alleen de rode kleur (bijvoorbeeld 'red')
    color_to_track = 'blue'

    color_contouring(True, transformer, color_to_track)
