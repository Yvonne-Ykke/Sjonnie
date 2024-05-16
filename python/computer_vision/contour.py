import numpy as np
import cv2 as cv
import math

developing = False

if developing:
    cap = cv.VideoCapture(0)
else:
    cap = cv.VideoCapture(1)

while(True):
    ret,im = cap.read()
    if im is None:
        break
    
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(imgray,(5,5),0)

    ret, threshoog = cv.threshold(blur, 110, 200, cv.THRESH_BINARY)

    #general object shape
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
            print (area, factor, holes)

            if area > 0:
                cv.drawContours(im, [cnt], -1, (255, 0, 0), 3);
            if area < 3000:
                if area > 550:
                    if holes < 150:
                        if factor < 0.8:
                            cv.drawContours(im, [cnt], -1, (0, 0, 255), 3);
                        elif factor > 0.8:
                            cv.drawContours(im, [cnt], -1, (0, 255, 0), 3);

    if developing:
        cv.imshow('thres', threshoog)
        cv.imshow('contour_vision', imgray)
        cv.imshow('computer_vision',im)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

    else:
        cv.imwrite('thres.jpg', im)

        cap.release()
        cv.destroyAllWindows()
        break
