import cv2
import numpy as np
from matplotlib import pyplot as plt

# Define camera coordinates (x, y) and corresponding real-world coordinates (X, Y)
camera_coords = np.array([
    [161, 315],
    [171, 389],
    [181, 462],
    [225, 307],
    [235, 381],
    [245, 454],
    [288, 297],
    [299, 370],
    [311, 444]
], dtype="float32")

real_world_coords = np.array([
    [-140, 375],
    [-140, 295],
    [-140, 215],
    [-70, 374],
    [-70, 294],
    [-70, 214],
    [0, 375],
    [0, 298],
    [0, 219]
], dtype="float32")

# Ensure the coordinates are in the correct shape
camera_coords = np.array(camera_coords, dtype="float32")
real_world_coords = np.array(real_world_coords, dtype="float32")

# Compute the homography matrix
homography_matrix, _ = cv2.findHomography(camera_coords, real_world_coords)

def convert_coordinates(camera_points, matrix):
    camera_points = np.array(camera_points, dtype="float32")
    camera_points = np.array([camera_points])  # Reshape for perspectiveTransform
    real_world_points = cv2.perspectiveTransform(camera_points, matrix)
    return real_world_points[0]

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

def detect_black_dots(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    coordinates = []
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        if w < 20 and h < 20:  # Filter out larger blobs
            coordinates.append((x + w//2, y + h//2))
    return coordinates

def annotate_image(image, coordinates, real_world_coordinates):
    annotated_image = image.copy()
    for (cam_coord, real_coord) in zip(coordinates, real_world_coordinates):
        x, y = cam_coord
        rw_x, rw_y = real_coord
        cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(annotated_image, f"({rw_x:.2f}, {rw_y:.2f})", (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return annotated_image

def main():
    image = capture_photo()
    if image is None:
        return
    
    camera_coordinates = detect_black_dots(image)
    
    real_world_coordinates = convert_coordinates(camera_coordinates, homography_matrix)
    
    print("Camera Coordinates:")
    for coord in camera_coordinates:
        print(coord)

    print("\nConverted Real-World Coordinates:")
    for coord in real_world_coordinates:
        print(coord)
    
    annotated_image = annotate_image(image, camera_coordinates, real_world_coordinates)
    
    # Display the annotated image
    plt.imshow(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
    plt.title('Annotated Image')
    plt.axis('off')
    plt.show()

# Run the main function
if __name__ == "__main__":
    main()
