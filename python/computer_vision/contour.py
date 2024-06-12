import numpy as np
import cv2 as cv
import math
import color_recognition
import time
import os
import pathlib


def contouring(developing):
    cap = cv.VideoCapture(0)

    while(True):
        ret,im = cap.read()
        if im is None:
            break
        
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
                    if 0.05 < factor < 0.12: #curved scissors
                        #print (area, factor, holes)
                        cv.drawContours(im, [cnt], -1, (255, 0, 0), 3)
                        
                        print("curved scissors")
                    elif 0.12 < factor < 0.2: #straight scissors
                        #print (area, factor, holes)
                        cv.drawContours(im, [cnt], -1, (0, 255, 255), 3)
                        print("straight scissors")               

        cv.imshow('thres', threshoog)
        cv.imshow('contour_vision', imgray)
        cv.imshow('computer_vision',im)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

def draw_scissors(area, factor, img, cnt, child, color_name, bgr, developing=None):
    if area > 500 and area < 100000:
        x, y, w, h = cv.boundingRect(cnt)
        if 0.05 < factor < 0.12: #curved scissors
            #print (area, factor, holes)

            if developing:
                cv.drawContours(img, [cnt], -1, bgr, 3)
                cv.rectangle(img, (x, y), (x+w, y+h), bgr, 3)
                cv.putText(img, 'scissors', (x+w, y+h), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
            print("curved scissors " + color_name)
        elif 0.12 < factor < 0.2: #straight scissors
            #print (area, factor, holes)
            if developing:
                cv.drawContours(img, [cnt], -1, bgr, 3)
                cv.rectangle(img, (x, y), (x+w, y+h), bgr, 3)
                cv.putText(img, 'straight scissors', (x+w, y+h), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
            print("straight scissors " + color_name)

        M = cv.moments(cnt)
        if child <= 0:
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv.circle(img, (cx, cy), 5, (0, 255, 255), -1)

def color_contouring(developing, detection):
    cap = cv.VideoCapture(0)

    # if detection == "direction":
        # get_direction(area, factor, img, cnt, color_name, bgr)

    while(True):
        ret,img = cap.read()
        if img is None:
            break
        
        color_masks = color_recognition.masks(img)

        for color_name, mask, bgr in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            #cv.imshow(color_name, res)

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
                    draw_scissors(area, factor, img, cnt, child, color_name, bgr, developing)
                    if area > 500 and area < 100000:
                        if detection == "scissors":
                            draw_scissors(area, factor, img, cnt, child, color_name, bgr)

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


        time.sleep(0.1)
        
        if developing:
            cv.imshow("image", img)
            cv.imshow('thres', threshoog)
            
        if cv.waitKey(1) & 0xFF == ord('q'):
            img.release()
            #cv.destroyAllWindows()
            break

        

if __name__ == "__main__":
    contouring(False)
