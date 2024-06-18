import cv2 as cv

def check_available_cameras():
    num_cameras = 10  # Aangenomen aantal camera's dat we willen controleren
    for i in range(num_cameras):
        cap = cv.VideoCapture(i)
        if not cap.isOpened():
            print(f"Camera {i}: niet beschikbaar")
        else:
            print(f"Camera {i}: beschikbaar")
            cap.release()

if __name__ == "__main__":
    check_available_cameras()
