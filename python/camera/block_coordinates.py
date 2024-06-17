import numpy as np
import cv2 as cv
import math
import sys
import os
import time
import color_recognition as color_definitions 
from coordinate_transformation import CoordinateTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules from the movement directory
import movement.robot_arm_parameters as robot_arm_parameters
import movement.angle_calculator as angle_calculator
import movement.client as client



# Callback function for trackbars
def nothing(x):
    pass

def create_trackbars():
    cv.namedWindow('settings')
    cv.createTrackbar('Min Area', 'settings', 1000, 1500, nothing)
    cv.createTrackbar('Max Area', 'settings', 1500, 3000, nothing)

def get_trackbar_values():
    min_area = cv.getTrackbarPos('Min Area', 'settings')
    max_area = cv.getTrackbarPos('Max Area', 'settings')
    return min_area, max_area

def color_contouring(developing, transformer): 
    cap = cv.VideoCapture(0)
    create_trackbars()

    while True:
        ret, img = cap.read()
        if img is None:
            break
        
        color_masks = color_definitions.masks(img)

        for color_name, mask, bgr in color_masks:
            res = cv.bitwise_and(img, img, mask=mask)
            imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(imgray, (3, 3), 0)
            ret, threshoog = cv.threshold(imgray, 1, 255, cv.THRESH_BINARY)
            contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            if hierarchy is not None:
                hierarchy = hierarchy[0]

            min_area, max_area = get_trackbar_values()
            
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                area = cv.contourArea(cnt)
                if min_area < area < max_area:
                    M = cv.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        real_world_coords = transformer.convert_coordinates([(cX, cY)])
                        print(f"Camera Coordinates: ({cX}, {cY}) -> Real World Coordinates: {real_world_coords}")
                        cv.drawContours(img, [cnt], -1, (0, 255, 0), 3)  # Draw contour in green
                        cv.circle(img, (cX, cY), 5, (0, 0, 255), -1)  # Draw centroid in red
                        cv.putText(img, f"{real_world_coords[0][0]:.2f}, {real_world_coords[0][1]:.2f}", (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                        # No need to send arm coordinates here
                        shoulder, elbow = angle_calculator.calculate_arm_angles(real_world_coords[0][0], real_world_coords[0][1], 300, 0, 0)
                        client.send_arm_angles_to_robot(shoulder, -elbow)
                        print(f"Shoulder: {shoulder}, Elbow: {elbow}")
                        time.sleep(1000)
        if developing:
            cv.imshow("image", img)

        key = cv.waitKey(1)  # Capture key press event
        if key == ord('q'):
            cap.release()
            cv.destroyAllWindows()


if __name__ == "__main__":
    # Define camera coordinates (x, y) and corresponding real-world coordinates (X, Y)
    camera_coords = [
        [202, 204],
        [209, 277],
        [217, 352],
        [266, 179],
        [274, 269],
        [282, 345],
        [330, 190],
        [339, 262],
        [347, 337]
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

    # Initialize the transformer
    transformer = CoordinateTransformer(camera_coords, real_world_coords)

    color_contouring(True, transformer)