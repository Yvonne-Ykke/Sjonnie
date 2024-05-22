import numpy as np
import cv2 as cv

developing = True

class Color:
    def __init__(self, name, low_hsv, high_hsv, low_hsv2 = None, high_hsv2 = None):
        self.name = name
        self.low_hsv = low_hsv
        self.high_hsv = high_hsv
        self.low_hsv2 = low_hsv2
        self.high_hsv2 = high_hsv2

colors = [
    Color("blue", [90, 45, 45], [135, 255, 255]),
    Color("red", [0, 80, 80], [15, 255, 255], [165, 80, 80], [179, 255, 255]),
    Color("green", [37, 30, 30], [90, 255, 255]),
    Color("yellow", [16, 100, 100], [36, 255, 255]),
    # TODO: Add more colors
]

def masks(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    color_masks = []
    for color in colors:
        mask = np.zeros_like(frame)
        mask = cv.inRange(hsv, np.array(color.low_hsv), np.array(color.high_hsv))

        if np.array(color.low_hsv2) is not None and color.high_hsv2 is not None:
            mask2 = cv.inRange(hsv, np.array(color.low_hsv2), np.array(color.high_hsv2))
            mask = mask | mask2
                                       
        color_masks.append((color.name.capitalize(), mask))
    return color_masks

def detect(developing):
    if developing:
        cap = cv.VideoCapture(0)
    else:
        cap = cv.VideoCapture(1)
    
    while(True):
        ret,img = cap.read()
        if img is None:
            break
        cv.imshow("image", img)
        color_masks = masks(img)
        results = []
        for color_name, mask in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            results.append(res)
            cv.imshow(color_name, res)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break
        

if __name__ == "__main__":
    detect()

