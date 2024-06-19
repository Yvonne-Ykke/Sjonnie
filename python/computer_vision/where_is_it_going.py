import cv2
import numpy as np
from color_recognition import colors, Color
from scipy.stats import linregress

# Function to detect the rectangle of a given color and find its center
def detect_color_rectangle(frame, color, min_area=500):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the color range for the given color
    lower_color = np.array(color.low_hsv)
    upper_color = np.array(color.high_hsv)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    
    if color.low_hsv2 and color.high_hsv2:
        lower_color2 = np.array(color.low_hsv2)
        upper_color2 = np.array(color.high_hsv2)
        mask2 = cv2.inRange(hsv, lower_color2, upper_color2)
        mask = cv2.bitwise_or(mask, mask2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on approximate rectangle shape and minimum area
    rect_contours = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
        if len(approx) == 4 and cv2.contourArea(contour) > min_area:
            rect_contours.append(contour)

    if rect_contours:
        # Find the largest rectangular contour
        largest_contour = max(rect_contours, key=cv2.contourArea)
        
        # Get the bounding box around the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate the center of the rectangle
        center_x, center_y = x + w // 2, y + h // 2
        
        return largest_contour, (center_x, center_y)
    return None, None

# Initialize video capture
cap = cv2.VideoCapture(0)

prev_center = None
direction = ""
min_speed_threshold = 2  # Minimum speed to consider for movement
selected_color = colors[0]  # Default to the first color in the list

def track_color_movement(selected_color):
    global prev_center

    # Initialize variables
    centroids = []  # List to store centroids
    arrow_scale_factor = 5  # Scale factor for arrow length

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        contour, center = detect_color_rectangle(frame, selected_color)

        if center:
            # Draw the actual contour around the detected object in the BGR color
            cv2.drawContours(frame, [contour], -1, selected_color.bgr, 2)
            
            if prev_center:
                # Determine the movement direction
                dx = center[0] - prev_center[0]
                dy = center[1] - prev_center[1]
                speed = np.sqrt(dx**2 + dy**2)

                if speed > min_speed_threshold:
                    # Store the current centroid in the list every half second
                    if len(centroids) == 0 or len(centroids) % 15 == 0:  # Store every 15 frames (0.5 seconds at 30 fps)
                        centroids.append(center)

                    # Draw all stored centroids
                    for centroid in centroids:
                        cv2.circle(frame, centroid, 3, (255, 0, 0), -1)  # Draw a filled circle
                    
                    # Regression line calculation
                    if len(centroids) >= 2:
                        points_for_regression = np.array(centroids[-10:])  # Take the last 10 centroids
                        x_values = points_for_regression[:, 0]
                        y_values = points_for_regression[:, 1]

                        # Check if all x_values are the same (avoid division by zero)
                        if np.all(x_values == x_values[0]):
                            slope = 0  # Handle case where all x-values are the same
                        else:
                            slope, intercept, _, _, _ = linregress(x_values, y_values)
                    
                        # Predict points along the regression line
                        predicted_points = []
                        for i in range(1, 6):  # Extrapolate 5 points ahead
                            next_x = int(center[0] + i * 0.1 * dx)
                            next_y = int(slope * next_x + intercept)
                            predicted_points.append((next_x, next_y))

                        # Draw the predicted points
                        cv2.polylines(frame, [np.array(predicted_points, dtype=np.int32)], False, (255, 0, 0), 2)

                else:
                    direction = "No movement detected"

            else:
                direction = "No movement detected"

            prev_center = center

            # Display the direction on the frame
            cv2.putText(frame, f"Direction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Print the current color name on the frame
        cv2.putText(frame, f"Color: {selected_color.name}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Change color detection based on key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            selected_color = colors[0]
            centroids.clear()  # Clear centroids list when changing color
        elif key == ord('2'):
            selected_color = colors[1]
            centroids.clear()
        elif key == ord('3'):
            selected_color = colors[2]
            centroids.clear()
        elif key == ord('4'):
            selected_color = colors[3]
            centroids.clear()
        elif key == ord('5'):
            selected_color = colors[4]
            centroids.clear()
        # Add more elif statements for additional colors if needed

        # Wait for half a second (500 milliseconds)
        cv2.waitKey(500)

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

# Example of calling the function with the initial selected color
if __name__ == "__main__":
    track_color_movement(colors[0])  # Start tracking with the initial color (e.g., blue)
