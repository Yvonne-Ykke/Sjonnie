import  color_recognition
import contour

developing = True

def main():
    color_recognition.detect(developing)
    contour.countouring(developing)

if __name__ == "__main__":
    main()