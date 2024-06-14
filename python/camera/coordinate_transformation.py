# coordinate_transformer.py

import cv2
import numpy as np

class CoordinateTransformer:
    def __init__(self, camera_coords, real_world_coords):
        self.camera_coords = np.array(camera_coords, dtype="float32")
        self.real_world_coords = np.array(real_world_coords, dtype="float32")
        self.homography_matrix, _ = cv2.findHomography(self.camera_coords, self.real_world_coords)
    
    def capture_photo(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Error: Could not open camera.")
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise Exception("Error: Could not capture image.")
        return frame
    
    def detect_black_dots(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        coordinates = []
        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)
            if w < 20 and h < 20:  # Filter out larger blobs
                coordinates.append((x + w//2, y + h//2))
        return coordinates
    
    def convert_coordinates(self, camera_points):
        camera_points = np.array(camera_points, dtype="float32")
        camera_points = np.array([camera_points])  # Reshape for perspectiveTransform
        real_world_points = cv2.perspectiveTransform(camera_points, self.homography_matrix)
        return real_world_points[0]
    
    def get_real_world_coordinates(self):
        image = self.capture_photo()
        camera_coordinates = self.detect_black_dots(image)
        real_world_coordinates = self.convert_coordinates(camera_coordinates)
        
        return camera_coordinates, real_world_coordinates
