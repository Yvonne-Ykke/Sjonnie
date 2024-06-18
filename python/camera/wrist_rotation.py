import math
# De shouder input heeft een hoek tussen -130 en 130 graden en de elbow input is tussen de -150 en 150.
# De tweede hoek is gebaseerd op de eerste hoek. als beide op 0 zijn, staat de robot arm recht naar voren. 
WRIST = 88

def calculate_wrist_rotation(shoulder_angle, elbow_angle, target_rotation):
    forearm_angle_deg = shoulder_angle + elbow_angle
    forearm_angle_deg = (forearm_angle_deg + 180) % 360 - 180
    print(f"Forearm angle: {forearm_angle_deg:.2f} degrees")
    wrist_rotation = forearm_angle_deg - target_rotation
    wrist_rotation = (wrist_rotation + 180) % 360 - 180
    print(f"Wrist rotation: {wrist_rotation:.2f} degrees")
    
    return wrist_rotation

#calculate_wrist_rotation(0, 0, 70)

    
# import cv2
# import numpy as np

# def detect_orientation():
#     cap = cv2.VideoCapture(0)
    
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         # Convert frame to grayscale
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
#         # Apply GaussianBlur to reduce noise and improve contour detection
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
#         # Apply Canny Edge Detection
#         edged = cv2.Canny(blurred, 50, 150)
        
#         # Find contours
#         contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         for contour in contours:
#             if cv2.contourArea(contour) > 100:  # Filter small contours
#                 # Get the minimum area rectangle
#                 rect = cv2.minAreaRect(contour)
#                 box = cv2.boxPoints(rect)
#                 box = np.int0(box)
                
#                 # Draw the contour and the rectangle
#                 cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
                
#                 # Get the angle from the rectangle
#                 angle = rect[2]
#                 if angle < -45:
#                     angle = 90 + angle
                
#                 # Display the angle on the frame
#                 cv2.putText(frame, f"Angle: {angle:.2f}", (int(rect[0][0]), int(rect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()

# Run the function
