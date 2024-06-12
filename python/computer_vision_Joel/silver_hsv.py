import cv2
import numpy as np

def nothing(x):
    pass

def detect_color(img, h_low, h_high, s_low, s_high, v_low, v_high):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for the color in HSV
    lower_bound = np.array([h_low, s_low, v_low])
    upper_bound = np.array([h_high, s_high, v_high])

    # Create mask using the inRange function
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply the mask to the original image
    result = cv2.bitwise_and(img, img, mask=mask)

    return mask, result

def main():
    # Open the camera
    cap = cv2.VideoCapture(0)

    cv2.namedWindow('image')

    # Create trackbars for HSV ranges
    cv2.createTrackbar('H_low', 'image', 0, 179, nothing)
    cv2.createTrackbar('H_high', 'image', 179, 179, nothing)
    cv2.createTrackbar('S_low', 'image', 0, 255, nothing)
    cv2.createTrackbar('S_high', 'image', 255, 255, nothing)
    cv2.createTrackbar('V_low', 'image', 0, 255, nothing)
    cv2.createTrackbar('V_high', 'image', 255, 255, nothing)

    # Create trackbars for contour area limits
    cv2.createTrackbar('Min Area', 'image', 500, 10000, nothing)
    cv2.createTrackbar('Max Area', 'image', 100000, 200000, nothing)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        if not ret:
            break

        # Read the current position of trackbars for HSV range
        h_low = cv2.getTrackbarPos('H_low', 'image')
        h_high = cv2.getTrackbarPos('H_high', 'image')
        s_low = cv2.getTrackbarPos('S_low', 'image')
        s_high = cv2.getTrackbarPos('S_high', 'image')
        v_low = cv2.getTrackbarPos('V_low', 'image')
        v_high = cv2.getTrackbarPos('V_high', 'image')

        # Read the current position of trackbars for contour area limits
        min_area = cv2.getTrackbarPos('Min Area', 'image')
        max_area = cv2.getTrackbarPos('Max Area', 'image')

        # Detect the specified color
        mask, result = detect_color(frame, h_low, h_high, s_low, s_high, v_low, v_high)

        # Find contours in the mask
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if min_area < area < max_area:
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 3)  # Draw contour in green

        # Display the results
        cv2.imshow('mask', mask)
        cv2.imshow('image', frame)

        # Stop the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the camera and windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
