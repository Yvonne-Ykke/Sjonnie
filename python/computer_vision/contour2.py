import numpy as np
import cv2 as cv
import math

def countouring(developing):
    if developing:
        cap = cv.VideoCapture(0)
    else:
        cap = cv.VideoCapture(1)

    while(True):
        ret, im = cap.read()
        if im is None:
            break
        
        # Convert to grayscale
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blur = cv.GaussianBlur(imgray, (5, 5), 0)

        # Use Canny edge detection
        edges = cv.Canny(blur, 50, 150)

        # Dilate the edges to close gaps between edge segments
        kernel = np.ones((5, 5), np.uint8)
        dilated_edges = cv.dilate(edges, kernel, iterations=1)

        # Find contours
        contours, hierarchy = cv.findContours(dilated_edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        hierarchy = hierarchy[0] if hierarchy is not None else []

        for cnr in range(len(contours)):
            cnt = contours[cnr]
            area = cv.contourArea(cnt)
            perimeter = cv.arcLength(cnt, True)
            if perimeter > 0:
                factor = 4 * math.pi * area / (perimeter**2)
                holes = 0
                child = hierarchy[cnr][2] if len(hierarchy) > cnr else -1
                while child >= 0:
                    holes += cv.contourArea(contours[child])
                    child = hierarchy[child][0]
                print(area, factor, holes)

                # Draw contours based on criteria
                if area > 0:
                    cv.drawContours(im, [cnt], -1, (255, 0, 0), 3)
                if area < 3000:
                    if area > 550:
                        if holes < 150:
                            if factor < 0.8:
                                cv.drawContours(im, [cnt], -1, (0, 0, 255), 3)
                            elif factor > 0.8:
                                cv.drawContours(im, [cnt], -1, (0, 255, 0), 3)

        if developing:
            cv.imshow('Edges', edges)
            cv.imshow('Dilated Edges', dilated_edges)
            cv.imshow('Contour Vision', imgray)
            cv.imshow('Computer Vision', im)

            if cv.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv.destroyAllWindows()
                break
        else:
            cv.imwrite('thres.jpg', im)
            cap.release()
            cv.destroyAllWindows()
            break

# Example usage:
countouring(developing=True)
