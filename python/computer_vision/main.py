import  color_recognition
import contour
import direction
from color_recognition import colors
import os
import cv2 as cv

DEVELOPING = True
COLORS = "colors"
SCISSORS = "scissors"
DIRECTION= "direction"
TARGET = "target"


def main():
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video capture")
        return

    while True:
        ret, img = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        contour.color_contouring(DEVELOPING, SCISSORS, 0, img)



# def main():
#     #color_recognition.detect(developing)
#     #contour.contouring(developing)
#     cap = cv.VideoCapture(0)


#     if not cap.isOpened():
#         print("Error: Could not open video capture")
#         return
    

#     ret,img = cap.read()
#     #info = 

#     contour.color_contouring(DEVELOPING, SCISSORS, 0, img)

#     # direction.track_color_movement(colors[0])

#     # contour.contouring(developing)
    
#     #Send infromatie naar esp32
#     #info = contour.color_contouring(developing)
#     #comm.send(info)


if __name__ == "__main__":
    main()