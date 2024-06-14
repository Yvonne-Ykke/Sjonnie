import cv2
import numpy as np
from matplotlib import pyplot as plt

# Function to capture a photo using the default camera
def capture_photo():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Error: Could not capture image.")
        return None
    return frame

# Function to detect black dots in the image
def detect_black_dots(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    coordinates = []
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        if w < 10 and h < 10:  # Filter out larger blobs
            coordinates.append((x + w//2, y + h//2))
    return coordinates

# Function to annotate image with coordinates
def annotate_image(image, coordinates):
    annotated_image = image.copy()
    for (x, y) in coordinates:
        cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(annotated_image, f"({x}, {y})", (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return annotated_image

# Main function
def main():
    image = capture_photo()
    if image is None:
        return
    
    coordinates = detect_black_dots(image)
    
    print("Coordinates of black dots:")
    for coord in coordinates:
        print(coord)
    
    annotated_image = annotate_image(image, coordinates)
    
    # Display the annotated image
    plt.imshow(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
    plt.title('Annotated Image')
    plt.axis('off')
    plt.show()

# Run the main function
if __name__ == "__main__":
    main()
