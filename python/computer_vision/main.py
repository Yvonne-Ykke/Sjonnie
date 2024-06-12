import  color_recognition
import contour
import os

DEVELOPING = True

def main():
    #color_recognition.detect(developing)
    #contour.contouring(developing)
    
    #info = 
    contour.color_contouring(DEVELOPING, "colors")
    # contour.contouring(developing)
    
    #Send infromatie naar esp32
    #info = contour.color_contouring(developing)
    #comm.send(info)


if __name__ == "__main__":
    main()