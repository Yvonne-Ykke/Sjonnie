import  color_recognition
import contour
import direction
from color_recognition import colors
import os

DEVELOPING = True
COLORS = "colors"
SCISSORS = "scissors"
DIRECTION= "direction"
TARGET = "target"


def main():
    #color_recognition.detect(developing)
    #contour.contouring(developing)
    
    #info = 

    contour.color_contouring(DEVELOPING, SCISSORS, 0)

    # direction.track_color_movement(colors[0])

    # contour.contouring(developing)
    
    #Send infromatie naar esp32
    #info = contour.color_contouring(developing)
    #comm.send(info)


if __name__ == "__main__":
    main()