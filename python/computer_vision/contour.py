import numpy as np
import cv2 as cv
import math
import color_recognition
import time
import os
import pathlib
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules from the movement directory
import movement.robot_arm_parameters as robot_arm_parameters
from movement.robot_arm import RobotArm
import movement.angle_calculator as angle_calculator
import movement.client as client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import camera.coordinate_transformation as ct
from camera.coordinate_transformation import CoordinateTransformer
from camera.coordinates_check import camera_coords, real_world_coords
import camera.wrist_rotation as wrist_rotation

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import controlling.python_servo_controller.controls as controls

convertion_rate = 1.1398

def adjust_centroid_to_contour(centroid, contour):
    # Find the nearest point on the contour to the centroid
    nearest_point = None
    min_distance = float('inf')
    for point in contour:
        distance = np.linalg.norm(np.array(point[0]) - np.array(centroid))
        if distance < min_distance:
            min_distance = distance
            nearest_point = point[0]

    # Move the centroid towards the nearest point by a small step
    direction_vector = np.array(nearest_point) - np.array(centroid)
    new_centroid = np.array(centroid) + direction_vector * 0.1  # Move 10% of the distance

    return new_centroid[0], new_centroid[1]

def curved_or_straight(img, centroid, contour, bgr):
    result = cv.pointPolygonTest(contour, centroid, False)

    if result > 0: #straight scissors
        #print (area, factor, holes)
        cv.drawContours(img, [contour], -1, (0, 255, 255), 3)
        cv.putText(img, 'straight scissors', (contour[0][0][0], contour[0][0][1]), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
        print("straight scissors")
        return "straight"
    elif result < 0: #curved scissors
        #print (area, factor, holes)
        cv.drawContours(img, [contour], -1, (255, 0, 0), 3)
        cv.putText(img, 'curved scissors', (contour[0][0][0], contour[0][0][1]), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
        print("curved scissors")
        return "curved"
    else:
        print("Schaar?") 

def contouring(im, developing):
    cx,cy,angle, shape = 0,0,0,None
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(imgray,(3,3),0)

    ret, threshoog = cv.threshold(blur, 120, 200, cv.THRESH_BINARY)

    contours, hierarchy = cv.findContours(threshoog, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    hierarchy = hierarchy[0]

    for cnr in range(len(contours)):
        cnt = contours [cnr]
        area = cv.contourArea(cnt)
        perimeter = cv.arcLength(cnt, True)

        if perimeter > 0:
            factor = 4 * math.pi * area / perimeter**2
            holes = 0
            child = hierarchy[cnr][2]
            while child >= 0:
                holes += cv.contourArea(contours[child])
                child = hierarchy[child][0]
            
            if area > 500 and area < 100000:
                M = cv.moments(cnt)  
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv.circle(im, (cX, cY), 5, (0, 0, 255), -1) 
                
                centroid = (cX, cY)

                shape = curved_or_straight(im, centroid, cnt, (0, 0, 255))
                        
                x, y, w, h = cv.boundingRect(cnt)
                cv.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)

                rect = cv.minAreaRect(cnt)
                angle = rect[2]
                if angle < -45:
                    angle += 90

                cv.putText(im, f'Angle: {angle:.2f}', (int(rect[0][0]), int(rect[0][1])),
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)      

    if developing:
        cv.imshow('thres', threshoog)
        cv.imshow('contour_vision', imgray)
        cv.imshow('computer_vision',im)
    return cX, cY, angle, shape


def move_robot(serial_connection, x, y, object_angle, shape):
    transformer = CoordinateTransformer(camera_coords, real_world_coords, convertion_rate)
    real_coords = transformer.convert_coordinates([(x, y)])[0]
    shoulder, elbow = angle_calculator.main(real_coords[0], real_coords[1])
    if shoulder is not None and elbow is not None:
        wrist_angle = wrist_rotation.calculate_wrist_rotation(shoulder, -elbow, object_angle)
        time.sleep(10)
        RobotArm.move_to_position(shoulder, -elbow, wrist_angle, serial_connection)
        time.sleep(8)
        controls.auto_grab('grab', serial_connection, spd=20)
        if shape == "straight":
            shoulder2, elbow2 = angle_calculator.main(290,-110)
            wrist_angle = -34
        else:
            shoulder2, elbow2 = angle_calculator.main(-390,-60)
            wrist_angle = 104
        time.sleep(10)
        RobotArm.move_to_position(shoulder2, -elbow2, wrist_angle, serial_connection)
        time.sleep(10)
        controls.auto_grab('drop', serial_connection, spd=20)      
        print(f"Shoulder: {shoulder}, Elbow: {elbow}", f"Wrist: {wrist_angle}")
        time.sleep(10)
    else:
        print("Unable to calculate shoulder or elbow angle.")

def draw_scissors(area, factor, img, cnt, child, color_name, bgr, developing=None):
    if area > 500 and area < 100000:
        M = cv.moments(cnt)  
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv.circle(img, (cX, cY), 5, (0, 0, 255), -1)  
        centroid = cX, cY

        shape = curved_or_straight(img, centroid, cnt, bgr)

        x, y, w, h = cv.boundingRect(cnt)
        cv.rectangle(img, (x, y), (x + w, y + h), bgr, 2)

        rect = cv.minAreaRect(cnt)
        angle = rect[2]
        if angle < -45:
            angle += 90

        cv.putText(img, f'Angle: {angle:.2f}', (int(rect[0][0]), int(rect[0][1])),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        M = cv.moments(cnt)
        if child <= 0:
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv.circle(img, (cx, cy), 5, (0, 255, 255), -1)
                if shape == "curved":
                    cx, cy = adjust_centroid_to_contour(centroid, cnt)
                return cx, cy, angle, shape

def detect(color_name, img, mask, bgr, developing, detection):
    cx,cy,angle, shape = 0,0,0,None
    res = cv.bitwise_and(img,img, mask= mask)
    imgray2 = cv.cvtColor(res, cv.COLOR_HSV2BGR)
    imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(imgray,(3,3),0)
    ret, threshoog = cv.threshold(imgray, 1, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    if hierarchy is not None:
        hierarchy = hierarchy[0]
    
    for cnr in range(len(contours)):
        cnt = contours [cnr]
        area = cv.contourArea(cnt)
        perimeter = cv.arcLength(cnt, True)
        if perimeter > 0:
            factor = 4 * math.pi * area / perimeter**2 
            holes = 0
            child = hierarchy[cnr][2]
            while child >= 0:
                holes += cv.contourArea(contours[child])
                child = hierarchy[child][0]
            #print (area, factor, holes)
            #print (child)
            if area > 500 and area < 100000:
                if detection == "scissors":
                    cx, cy, angle, shape = draw_scissors(area, factor, img, cnt, child, color_name, bgr, developing)

                elif detection == "colors":
                    if 0.4 < factor < 0.7:
                        x, y, w, h = cv.boundingRect(cnt)
                        cv.drawContours(img, [cnt], -1, bgr, 3)
                        cv.rectangle(img, (x, y), (x+w, y+h), bgr, 3)
                        cv.putText(img, color_name, (x+w, y+h), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
                elif detection == "target":
                    print("not yet implemented")
    if developing:
        cv.imshow(color_name, res)
    if cx == 0 or cy == 0 or angle == 0:
        print("No object detected")

    return cx, cy, angle, shape


def color_contouring(serial_connection, developing, detection, color, img, dynamic):

    color_masks = color_recognition.masks(img)
    if color != 0:
        color_name, mask, bgr = color_masks[color - 1]
        cx, cy ,angle, shape = detect(color_name, img, mask, bgr, developing, detection)
        if cx != 0 and cy != 0 and angle != 0:
            move_robot(serial_connection, cx, cy, angle, shape)
            time.sleep(2)
            
    else:
        cx, cy, angle, shape = contouring(img, developing)
        if not dynamic:
            #TODO: Implement movement
            if cx != 0 and cy != 0 and angle != 0:
                move_robot(serial_connection, cx, cy, angle, shape)
                time.sleep(2)
            print("movement to be implemented")

    time.sleep(0.1)
        
    if developing:
        cv.imshow("image", img)
            
    if cv.waitKey(1) & 0xFF == ord('q'):
        img.release() 

if __name__ == "__main__":
    contouring(False)
