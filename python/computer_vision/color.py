import numpy as np
import cv2 as cv

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
            mask += cv.inRange(hsv, np.array(hsv_range[0]), np.array(hsv_range[1]))
            if hsv_range[2] is not None:
                mask2 += cv.inRange(hsv, np.array(hsv_range[2]), np.array(hsv_range[3]))
                mask = mask | mask2
                                       
        color_masks.append((color.name.capitalize(), mask))

        print(color_masks)
    return color_masks