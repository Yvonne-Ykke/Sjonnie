import numpy as np
import cv2 as cv


DEVELOPING = False

class Color:
    def __init__(self, name, low_hsv, high_hsv, bgr=None, low_hsv2=None, high_hsv2=None):
        self.name = name
        self.low_hsv = low_hsv
        self.high_hsv = high_hsv
        self.low_hsv2 = low_hsv2
        self.high_hsv2 = high_hsv2
        self.bgr = bgr

colors = [
    Color("blue", [80, 60, 0], [140, 255, 255], [255, 0, 0]),
    Color("red", [165, 70, 50], [175, 255, 255], [0, 0, 255]),
    Color("green", [40, 41, 74], [86, 255, 255], [0, 255, 0]),
    Color("yellow", [16, 80, 0], [36, 255, 255], [0, 255, 255]),
    Color("pink", [0, 70, 50], [15, 255, 255], [0, 50, 255], [160, 70, 50], [164, 255, 255]),
    Color("silver", [0, 0, 50], [360, 30, 100],[192, 192, 192])
]

def apply_clahe(frame):
    lab = cv.cvtColor(frame, cv.COLOR_BGR2Lab)
    l, a, b = cv.split(lab)
    
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    limg = cv.merge((cl, a, b))
    final = cv.cvtColor(limg, cv.COLOR_Lab2BGR)
    return final

def masks(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    color_masks = []
    for color in colors:
        mask = cv.inRange(hsv, np.array(color.low_hsv), np.array(color.high_hsv))
        if color.low_hsv2 is not None and color.high_hsv2 is not None:
            mask2 = cv.inRange(hsv, np.array(color.low_hsv2), np.array(color.high_hsv2))
            mask = mask | mask2
        color_masks.append((color.name.capitalize(), mask))
    return color_masks

def detect(developing):
    if developing:
        cap = cv.VideoCapture(1)
    else:
        cap = cv.VideoCapture(0)
    
    while(True):
        ret, img = cap.read()
        if img is None:
            break

        img = apply_clahe(img)
        
        cv.imshow("image", img)

        color_masks = masks(img)
        results = []
        for color_name, mask in color_masks:
            res = cv.bitwise_and(img, img, mask=mask)
            results.append(res)
            
            # if developing:
            cv.imshow(color_name, res)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break

if __name__ == "__main__":
    detect(DEVELOPING)

