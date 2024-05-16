import numpy as np
import cv2 as cv

developing = True

class Color:
    def __init__(self, name, hsv_range):
        self.name = name
        self.hsv_range = hsv_range

colors = [
    Color("blue", [[90, 45, 45], [135, 255, 255]]),
    Color("red", [[0, 80, 80], [15, 255, 255], [165, 80, 80], [179, 255, 255]]),
    Color("green", [[37, 30, 30], [90, 255, 255]]),
    # TODO: Add more colors
]

def masks(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    color_masks = []
    for color in colors:
        mask = np.zeros_like(frame)
        for hsv_range in color.hsv_range:
            mask = cv.inRange(hsv, np.array(hsv_range[0]), np.array(hsv_range[1]))
            if len(hsv_range) == 4:
                mask2 = cv.inRange(hsv, np.array(hsv_range[2]), np.array(hsv_range[3]))
                mask = mask | mask2
                                       
        color_masks.append((color.name.capitalize(), mask))
    return color_masks

cap = cv.VideoCapture(0)
while(True):
    ret,img = cap.read()
    if img is None:
        break
    cv.imshow("image", img)
    color_masks = masks(img)
    for color_name, mask in color_masks:
        res = cv.bitwise_and(img,img, mask= mask)
        cv.imshow(color_name, res)
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv.destroyAllWindows()
        break