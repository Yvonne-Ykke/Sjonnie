import  color_recognition
import contour
import os

#None = de webcam
#1 = je ingebouwde laptop webcam
#2 = een testfoto

developing = 2

def main():
    #color_recognition.detect(developing)
    #contour.contouring(developing)
    
    contour.color_contouring(developing)


    



if __name__ == "__main__":
    main()