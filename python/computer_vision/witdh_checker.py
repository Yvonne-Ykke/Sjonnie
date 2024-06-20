import cv2
import numpy as np

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def get_contour_widths(contour):
    min_y = min(contour, key=lambda x: x[0][1])[0][1]
    max_y = max(contour, key=lambda x: x[0][1])[0][1]
    widths = []
    for y in range(min_y, max_y, 10):  # 10 pixels interval
        points_at_y = [pt[0] for pt in contour if pt[0][1] == y]
        if points_at_y:
            min_x = min(points_at_y, key=lambda x: x[0])[0]
            max_x = max(points_at_y, key=lambda x: x[0])[0]
            width = max_x - min_x
            widths.append((y, width))
    return widths

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    # Verlaag de resolutie voor snellere verwerking
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            contour = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(contour)
            angle = rect[-1]
            if angle < -45:
                angle += 90

            rotated = rotate_image(frame, angle)
            gray_rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
            _, thresh_rotated = cv2.threshold(gray_rotated, 127, 255, cv2.THRESH_BINARY)
            contours_rotated, _ = cv2.findContours(thresh_rotated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours_rotated:
                contour_rotated = max(contours_rotated, key=cv2.contourArea)
                widths = get_contour_widths(contour_rotated)

                if widths:
                    max_width_y, max_width = max(widths, key=lambda x: x[1])
                    top_width = widths[0][1]
                    bottom_width = widths[-1][1]
                    if top_width > bottom_width:
                        text = "Breder aan de bovenkant"
                    else:
                        text = "Breder aan de onderkant"

                    for y, width in widths:
                        cv2.line(rotated, (int((rotated.shape[1] - width) / 2), y), (int((rotated.shape[1] + width) / 2), y), (0, 255, 0), 1)

                    cv2.putText(rotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow('Widths', rotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
