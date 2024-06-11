import numpy as np
import cv2 as cv
import os
import signal
from tkinter import Tk, Button, Frame, Label, Text, Scrollbar, END
from PIL import Image, ImageTk

# Calibration criteria and chessboard size
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
rows, cols = 7, 7  # Number of inner corners per chessboard row and column
objp = np.zeros((rows * cols, 3), np.float32)
objp[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)
objpoints = []
imgpoints = []

screenshot_folder = 'python/camera/calibration_images'
screenshot_count = 0
stop_camera = False
stop_program_flag = False

def setup_camera():
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        log_message("Failed to open camera")
        exit()
    return capture

def clear_screenshot_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            log_message(f'Failed to delete {file_path}. Reason: {e}')

def take_screenshot():
    global screenshot_count, stop_camera
    ret, frame = cap.read()
    if not ret:
        log_message("Failed to capture frame")
        return

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_has_chessboard, corners = cv.findChessboardCorners(gray, (rows, cols), None)

    if frame_has_chessboard:
        screenshot_path = os.path.join(screenshot_folder, f'screenshot_{screenshot_count}.png')
        cv.imwrite(screenshot_path, frame)
        log_message(f'Screenshot {screenshot_count + 1} saved.')
        screenshot_count += 1

        if screenshot_count >= 10:
            stop_camera = True
            log_message("Camera stopped after 10 screenshots.")
            cap.release()

def stop_program():
    global stop_program_flag
    stop_program_flag = True
    root.quit()

def setup_gui():
    global root, cap, label, text_widget
    root = Tk()
    root.title("Camera Calibration")

    # Create a frame for the video and the button
    frame = Frame(root)
    frame.pack()

    # Create a label for the video
    label = Label(frame)
    label.pack()

    # Create the button and make it 10x bigger
    btn_screenshot = Button(frame, text="Take Screenshot", command=take_screenshot, width=30, height=5)
    btn_screenshot.pack()

    # Create a text widget for logs
    text_frame = Frame(root)
    text_frame.pack(fill="both", expand=True)
    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    text_widget = Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)

    # Handle closing the window
    root.protocol("WM_DELETE_WINDOW", stop_program)

    return root

def log_message(message):
    text_widget.insert(END, message + "\n")
    text_widget.see(END)
    print(message)

def main_loop(cap, root):
    global stop_camera, stop_program_flag, label
    while not stop_program_flag:
        if stop_camera:
            cap.release()
            break

        ret, frame = cap.read()
        if not ret:
            log_message("Failed to capture frame")
            break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, (rows, cols), None)

        if ret:
            cv.drawChessboardCorners(frame, (rows, cols), corners, ret)

        # Convert the image to a format suitable for Tkinter
        img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        label.imgtk = imgtk
        label.configure(image=imgtk)

        root.update_idletasks()
        root.update()


def process_screenshots():
    if screenshot_count >= 10:
        log_message("Processing screenshots for calibration...")
        for i in range(screenshot_count):
            img_path = os.path.join(screenshot_folder, f'screenshot_{i}.png')
            img = cv.imread(img_path)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (rows, cols), None)

            if ret:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)

        if objpoints and imgpoints:
            calibrate_camera(gray.shape[::-1])
        else:
            log_message("No calibration data collected.")
    else:
        log_message("Not enough screenshots for calibration.")

def calibrate_camera(image_shape):
    log_message("Calibrating camera...")
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, image_shape, None, None)
    if ret:
        np.savez('calibration_data.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
        log_message("Camera calibration successful.")
        log_message(f"Camera matrix:\n{mtx}")
        log_message(f"Distortion coefficients:\n{dist}")
    else:
        log_message("Failed to calibrate camera")

def signal_handler(sig, frame):
    log_message("Interrupt received, stopping...")
    stop_program()

# Main script execution
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    os.makedirs(screenshot_folder, exist_ok=True)
    clear_screenshot_folder(screenshot_folder)
    cap = setup_camera()
    root = setup_gui()
    main_loop(cap, root)
    process_screenshots()
    cv.destroyAllWindows()

