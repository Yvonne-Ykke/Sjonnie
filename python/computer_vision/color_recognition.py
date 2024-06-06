import numpy as np
import cv2 as cv

class Color:
    def __init__(self, name, low_hsv, high_hsv, bgr = None, low_hsv2 = None, high_hsv2 = None):
        self.name = name
        self.low_hsv = low_hsv
        self.high_hsv = high_hsv
        self.low_hsv2 = low_hsv2
        self.high_hsv2 = high_hsv2
        self.bgr = bgr

colors = [
    Color("blue", [80, 60, 0], [140, 255, 255], [255, 0, 0]),
    Color("red", [0, 70, 0], [15, 255, 255], [175, 70, 60], [179, 255, 255], [0, 0, 255]),
    Color("green", [40, 41, 74], [86, 255, 255], [0, 255, 0]),
    Color("yellow", [16, 80, 0], [36, 255, 255], [0, 255, 255]),
    Color("pink", [167, 63, 100], [176, 255, 255], [0, 50, 255]),
    Color("silver", [10, 10, 100], [160, 255, 255],[170,169,173])


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
        cap = cv.VideoCapture(1)
    else:
        cap = cv.VideoCapture(0)
    
    while(True):
        ret,img = cap.read()
        if img is None:
            break
        
        if developing:
            cv.imshow("image", img)

        color_masks = masks(img)
        results = []
        for color_name, mask in color_masks:
            res = cv.bitwise_and(img,img, mask= mask)
            results.append(res)
            
            # if developing:
            cv.imshow(color_name, res)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv.destroyAllWindows()
            break
        

if __name__ == "__main__":
    detect(True)

