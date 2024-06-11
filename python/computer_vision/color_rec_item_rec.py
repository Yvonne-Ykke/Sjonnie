import numpy as np
import cv2 as cv
import math
import color_recognition
import time
import os
import pathlib



def color_contouring(developing):
    cap = cv.VideoCapture(0)
    
    while(True):
        ret,img = cap.read()
        if img is None:
            break
        
        color_masks = color_recognition.masks(img)

        results = []
        for color_name, mask, bgr in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            results.append(res)
            cv.imshow(color_name, res)

            #bgr = cv.cvtColor(bgr, cv.COLOR_HSV2BGR)
            imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(imgray,(5,5),0)

            ret, threshoog = cv.threshold(blur, 100, 255, cv.THRESH_BINARY_INV)

            contours, hierarchy = cv.findContours(threshoog, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            hierarchy = hierarchy[0]
            
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                area = cv.contourArea(cnt)
                perimeter = cv.arcLength(cnt, True)
                x, y, w, h = cv.boundingRect(cnt)

                if perimeter >= 0:
                    try:
                        factor = 4 * math.pi * area / perimeter**2 
                    except:
                        factor = 0
                    holes = 0
                    child = hierarchy[cnr][2]
                    while child >= 0:
                        holes += cv.contourArea(contours[child])
                        child = hierarchy[child][0]
                    #print (area, factor, holes)
                    #print (child)

                    
                    if area > 1000 and area < 100000 and factor > 0.01:
                        cv.drawContours(img, [cnt], -1, bgr, 1)

                        M = cv.moments(cnt)
                        if child <= 0:
                            if M['m00'] != 0:
                                cx = int(M['m10'] / M['m00'])
                                cy = int(M['m01'] / M['m00'])
                                cv.circle(img, (cx, cy), 5, (0, 255, 255), -1)

                        #count += 1
                        # TODO: CREATE RECTANGULAR CONTOUr
                        #cv.rectangle(img, (img, 0), (img + 100, 100), (0, 255,255), -1)
                        ##TODO: CHECK SHAPE IS RECTANGULAR
                        
                        min_contour_area = 500  # Define your minimum area threshold
                        large_contours = [cnt for cnt in contours if cv.contourArea(cnt) > min_contour_area]
                        for cnt in large_contours:
                            cv.rectangle(img, (x, y), (x+w, y+h), bgr, 3)
                            cv.putText(img, color_name, (x+w, y+h), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)
                            if 0.7 > factor > 0.2:
                                re = 'blokje'
                                cv.putText(img, re, (x+w, int(y+h*0.5)), cv.FONT_HERSHEY_SIMPLEX, 0.65, bgr, 2)

        time.sleep(0.1)
        cv.imshow("image", img)
        if developing:
            cv.imshow('thres', threshoog)
            
        if cv.waitKey(1) & 0xFF == ord('q'):
            img.release()
            cv.destroyAllWindows()
            break

        

if __name__ == "__main__":
    color_contouring(False)
