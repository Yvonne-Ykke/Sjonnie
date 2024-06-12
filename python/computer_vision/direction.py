import cv2
import numpy as np
from color_recognition import colors, Color
# Define the HSV color ranges for different colors
# color_ranges = {
#     'blue': (np.array([100, 150, 0]), np.array([140, 255, 255])),
#     'green': (np.array([40, 40, 40]), np.array([80, 255, 255])),
#     'red': (np.array([0, 150, 50]), np.array([10, 255, 255])),
#     'yellow': (np.array([20, 100, 100]), np.array([30, 255, 255]))
# }

# Function to detect the rectangle of a given color and find its center
def detect_color_rectangle(frame, color):
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

    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
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
arrow_scale_factor = 5  # Scale factor for the arrow length
selected_color = colors[0]  # Default to the first color in the list

def track_color_movement(selected_color):
    # Initialize video capture
    cap = cv2.VideoCapture(0)

    prev_center = None
    direction = ""
    min_speed_threshold = 5  # Minimum speed to consider for movement
    arrow_scale_factor = 0.5  # Scale factor for the arrow length

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
                    horizontal_direction = ""
                    vertical_direction = ""

                    if abs(dx) > min_speed_threshold:
                        if dx > 0:
                            horizontal_direction = "Right"
                        elif dx < 0:
                            horizontal_direction = "Left"
                    
                    if abs(dy) > min_speed_threshold:
                        if dy > 0:
                            vertical_direction = "Down"
                        elif dy < 0:
                            vertical_direction = "Up"

                    if horizontal_direction and vertical_direction:
                        direction = f"{vertical_direction}/{horizontal_direction}"
                    else:
                        direction = horizontal_direction or vertical_direction

                    # Calculate the end point for the arrow
                    arrow_end = (
                        int(center[0] + arrow_scale_factor * dx),
                        int(center[1] + arrow_scale_factor * dy)
                    )

                    # Draw the arrow
                    cv2.arrowedLine(frame, center, arrow_end, (0, 255, 0), 2, tipLength=0.3)
                else:
                    direction = "No movement detected"
            else:
                direction = "No movement detected"

            prev_center = center

            # Display the direction on the frame
            cv2.putText(frame, f"Direction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            direction = "No object detected"
            # Display the "No object detected" on the frame
            cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Change color detection based on key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
        elif key == ord('1'):
            selected_color = colors[0]
        elif key == ord('2'):
            selected_color = colors[1]
        elif key == ord('3'):
            selected_color = colors[2]
        elif key == ord('4'):
            selected_color = colors[3]
        elif key == ord('5'):
            selected_color = colors[4]
        # Add more elif statements for additional colors if needed

    # When everything is done, release the capture


# Example of calling the function with the initial selected color
if __name__ == "__main__":
    track_color_movement(colors[0])  # Start tracking with the initial color (e.g., blue)

