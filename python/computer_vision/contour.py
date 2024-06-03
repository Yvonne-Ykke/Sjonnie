import numpy as np
import cv2 as cv
import math
import color_recognition
import time
import os
import pathlib


def contouring(developing):
    if developing:
        cap = cv.VideoCapture(0)
    else:
        cap = cv.VideoCapture(1)

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
                

                if 0.05 < factor < 0.12: #curved scissors
                     #print (area, factor, holes)
                     cv.drawContours(im, [cnt], -1, (255, 0, 0), 3)
                elif 0.12 < factor < 0.2: #straight scissors
                    #print (area, factor, holes)
                    cv.drawContours(im, [cnt], -1, (0, 255, 255), 3)

                

        cv.imshow('thres', threshoog)
        cv.imshow('contour_vision', imgray)
        cv.imshow('computer_vision',im)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break



def color_contouring(developing):
    if developing:
        cap = cv.VideoCapture(0)
    else:
        cap = cv.VideoCapture(1)

    while(True):
        img = color_recognition.detect(developing)
        ret,img = cap.read()
        if img is None:
            break
        
        color_masks = color_recognition.masks(img)

        results = []
        for color_name, mask, bgr, count in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            results.append(res)
            cv.imshow(color_name, res)

            imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(imgray,(5,5),0)

            ret, threshoog = cv.threshold(blur, 45, 255, cv.THRESH_BINARY_INV)

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
                    #print (area, factor, holes)
                    #print (child)

                    
                    if area > 200 and area < 100000 and factor > 0.01:
                        cv.drawContours(img, [cnt], -1, bgr, 1)
                        count += 1

                        M = cv.moments(cnt)
                        if child <= 0:
                            if M['m00'] != 0:
                                cx = int(M['m10'] / M['m00'])
                                cy = int(M['m01'] / M['m00'])
                                cv.circle(img, (cx, cy), 5, (0, 255, 255), -1)

        time.sleep(0.1)
        cv.imshow("image", img)
        if developing:
            cv.imshow('thres', threshoog)
            
        if cv.waitKey(1) & 0xFF == ord('q'):
            img.release()
            cv.destroyAllWindows()
            break

        

if __name__ == "__main__":
    contouring(True)
