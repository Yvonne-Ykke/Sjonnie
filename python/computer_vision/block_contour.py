import numpy as np
import cv2 as cv
import math
import time
import color_recognition as color_definitions 

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

def contouring(developing):
    cap = cv.VideoCapture(0)
    
    create_trackbars()

    while True:
        ret, im = cap.read()
        if im is None:
            break
        
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(imgray, (3, 3), 0)

        ret, threshoog = cv.threshold(blur, 120, 200, cv.THRESH_BINARY)

        contours, hierarchy = cv.findContours(threshoog, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        if hierarchy is not None:
            hierarchy = hierarchy[0]

        # Get current positions of the sliders
        min_area, max_area = get_trackbar_values()

        for cnr in range(len(contours)):
            cnt = contours[cnr]
            area = cv.contourArea(cnt)
            
            if min_area < area < max_area:
                cv.drawContours(im, [cnt], -1, (0, 255, 0), 3)  # Draw contour in green

        if developing:
            # cv.imshow('thres', threshoog)
            cv.imshow('computer_vision', im)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

def color_contouring(developing):
    cap = cv.VideoCapture(0)

    create_trackbars()

    while True:
        ret, img = cap.read()
        if img is None:
            break
        
        color_masks = color_definitions.masks(img)

        for color_name, mask, bgr in color_masks:
            res = cv.bitwise_and(img, img, mask=mask)
            # cv.imshow(color_name, res)

            imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(imgray, (3, 3), 0)
            ret, threshoog = cv.threshold(imgray, 1, 255, cv.THRESH_BINARY)
            contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            if hierarchy is not None:
                hierarchy = hierarchy[0]

            # Get current positions of the sliders
            min_area, max_area = get_trackbar_values()
            
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                area = cv.contourArea(cnt)
                if min_area < area < max_area:
                    cv.drawContours(img, [cnt], -1, (0, 255, 0), 3)  # Draw contour in green

            print(f"Contour {color_name} drawn in green")

        time.sleep(0.1)
        
        if developing:
            cv.imshow("image", img)
            # cv.imshow('thres', threshoog)
            
        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

if __name__ == "__main__":
    color_contouring(True)