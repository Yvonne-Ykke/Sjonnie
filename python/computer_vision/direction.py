import cv2
import numpy as np

# Function to detect the blue rectangle and find its center
def detect_blue_rectangle(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range of blue color in HSV
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    contour, center = detect_blue_rectangle(frame)

    if center:
        # Draw the actual contour around the detected blue rectangle
        cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
        
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

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
