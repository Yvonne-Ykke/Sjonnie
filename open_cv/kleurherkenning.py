#kleurherkenning

import numpy as np
import cv2 as cv
import math

cap = cv.VideoCapture(0)

while(True):
    ret,img = cap.read()
    if img is None:
        break##laad t plaatje in
    # werkt met meerdere plaatjes
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_blue = np.array([90,45,45])
    upper_blue = np.array([135,255,255])
    
    # define range of red color in HSV
    lower_red = np.array([0,80,80])
    upper_red = np.array([15,255,255])
    # define range of red2 color in HSV
    lower_red2 = np.array([165,80,80])
    upper_red2 = np.array([179,255,255])
    
    # define range of green color in HSV
    lower_green = np.array([37,30,30])
    upper_green = np.array([90,255,255])
    
    maskb = cv.inRange(hsv, lower_blue, upper_blue)
    resb = cv.bitwise_and(img,img, mask= maskb)
    maskr1 = cv.inRange(hsv, lower_red, upper_red)
    maskr2 = cv.inRange(hsv, lower_red2, upper_red2)
    maskg = cv.inRange(hsv, lower_green, upper_green)
    resg = cv.bitwise_and(img,img, mask= maskg)

    combimaskr = maskr1 | maskr2
    resr = cv.bitwise_and(img,img, mask= combimaskr)

    cv.imshow('orginele foto',img)
    ##blauwe mask en result
    #cv.imshow('mask',maskb)
    cv.imshow('Blauw',resb)
    ##rode mask en result
    #cv.imshow('mask2',maskr)
    cv.imshow('Rood',resr)
    ##groene mask en result
    #cv.imshow('mask3',maskg)
    cv.imshow('Groen',resg)
    if cv.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv.destroyAllWindows()
        break


