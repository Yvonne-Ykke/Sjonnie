import numpy as np
import cv2 as cv
import math
import color_recognition
import time


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
                            if factor < 0.99:
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



def color_contouring(developing):
    #Get color image per mask
    if developing == 1:
        cap = cv.VideoCapture(0)
    elif developing == 2:
        cap = cv.imread(cv.samples.findFile("1.jpg"))
    else:
        cap = cv.VideoCapture(1)

    while(True):
        #img = color_recognition.detect(developing)

        ret,img = cap.read()
        if img is None:
            break
        
        color_masks = color_recognition.masks(img)
        gcount = 0
        rcount = 0
        bcount = 0
        ycount = 0
        results = []
        for color_name, mask in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            results.append(res)
            cv.imshow(color_name, res)

            imgray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(imgray,(5,5),0)

            ret, threshoog = cv.threshold(blur, 45, 255, cv.THRESH_BINARY_INV)

            #find contours of colored picture
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

                    if area > 200 and area < 100000:
                        if factor > 0.01:
                            if color_name == "Blue":
                                cv.drawContours(img, [cnt], -1, (255, 0, 0), 3);
                                bcount += 1
                            if color_name == "Green":
                                cv.drawContours(img, [cnt], -1, (0, 255, 0), 3);
                                gcount += 1
                            if color_name == "Red":
                                cv.drawContours(img, [cnt], -1, (0, 0, 255), 3);
                                rcount += 1
                            if color_name == "Yellow":
                                cv.drawContours(img, [cnt], -1, (0, 255, 255), 3);
                                ycount += 1
        print("Groen: " + str(gcount) + " Blauw: " + str(bcount) + " Rood: " + str(rcount) + " Geel: " + str(ycount))
        time.sleep(0.1)
        cv.imshow("image", img)
        if developing:
            cv.imshow('thres', threshoog)
            
            #cv.imshow('contour_vision', threshoog)

        if cv.waitKey(1) & 0xFF == ord('q'):
            img.release()
            cv.destroyAllWindows()
            break

        




if __name__ == "__main__":
    contouring()
