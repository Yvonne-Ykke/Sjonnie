import numpy as np
import cv2 as cv
import math
import sys
import os
import time
import color_recognition as color_definitions 
from coordinate_transformation import CoordinateTransformer
import wrist_rotation

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules from the movement directory
import movement.robot_arm_parameters as robot_arm_parameters
import movement.angle_calculator as angle_calculator
import movement.client as client
convertion_rate = 1.1398
#convertion_rate = 1.2

# Callback function for trackbars
def nothing(x):
    pass

def create_trackbars():
    cv.namedWindow('settings')
    cv.createTrackbar('Min Area', 'settings', 1000, 2000, nothing)
    cv.createTrackbar('Max Area', 'settings', 1500, 5000, nothing)

def get_trackbar_values():
    min_area = cv.getTrackbarPos('Min Area', 'settings')
    max_area = cv.getTrackbarPos('Max Area', 'settings')
    return min_area, max_area

def click_event(event, x, y, flags, params):
    if event == cv.EVENT_LBUTTONDOWN:
        real_world_coords = params.convert_coordinates([(x, y)])
        print(f"Clicked Coordinates: ({x}, {y}) -> Real World Coordinates: {real_world_coords}")
        
        # Extracting x and y from the first element of real_world_coords
        real_world_x, real_world_y = real_world_coords[0]
        shoulder, elbow = angle_calculator.main(real_world_x, real_world_y)

        if shoulder is not None and elbow is not None:
            client.send_arm_angles_to_robot(shoulder, -elbow, 45)
            print(f"Shoulder: {shoulder}, Elbow: {elbow}")
        else:
            print("Unable to calculate shoulder or elbow angle.")

def color_contouring(developing, transformer):
    cap = cv.VideoCapture(0)
    create_trackbars()

    cv.namedWindow('image')
    cv.setMouseCallback('image', click_event, param=transformer)

    while True:
        ret, img = cap.read()
        if img is None:
            break

        # Undistort the captured frame
        img = cv.undistort(img, transformer.mtx, transformer.dist)

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
                        # print(f"Camera Coordinates: ({cX}, {cY}) -> Real World Coordinates: {real_world_coords}")

                        # Get the minimum area rectangle
                        rect = cv.minAreaRect(cnt)
                        box = cv.boxPoints(rect)
                        box = np.int0(box)
                        objectAngle = rect[2]
                        width, height = rect[1]
                        if width < height:
                            objectAngle = objectAngle + 90  # Adjust the angle
                        # print(f"Angle: {angle} degrees")

                        # Draw the contour, centroid, and angle
                        cv.drawContours(img, [cnt], -1, (0, 255, 0), 3)  # Draw contour in green
                        cv.circle(img, (cX, cY), 5, (0, 0, 255), -1)  # Draw centroid in red
                        cv.drawContours(img, [box], 0, (255, 0, 0), 2)  # Draw rectangle in blue
                        cv.putText(img, f"{real_world_coords[0][0]:.2f}, {real_world_coords[0][1]:.2f}", (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                        cv.putText(img, f"Angle: {objectAngle:.2f}", (cX + 50, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)

                        # Check if the 's' key is pressed
                        key = cv.waitKey(1)
                        if key == ord('s'):
                            # Send the robot arm coordinates
                            shoulder, elbow = angle_calculator.main(real_world_coords[0][0], real_world_coords[0][1])
                            if elbow is not None:
                                wrist_angle = wrist_rotation.calculate_wrist_rotation(shoulder, -elbow, objectAngle)
                                client.send_arm_angles_to_robot(shoulder, -elbow, wrist_angle)
                                # print(f"Shoulder: {shoulder}, Elbow: {elbow}, wrist_angle: {wrist_angle}")
                                time.sleep(1)  # Delay for one second
                            else:
                                print("Unable to calculate elbow angle.")

        if developing:
            cv.imshow("image", img)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

if __name__ == "__main__":
    # Define camera coordinates (x, y) and corresponding real-world coordinates (X, Y)
    camera_coords = [
        [313, 223],
        [313, 293],
        [313, 363],
        [374, 223],
        [374, 293],
        [374, 363],
        [434, 223],
        [434, 293],
        [434,362]
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

    # Initialize the transformer with the conversion rate
    transformer = CoordinateTransformer(camera_coords, real_world_coords, convertion_rate)

    color_contouring(True, transformer)