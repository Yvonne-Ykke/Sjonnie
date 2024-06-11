import numpy as np
import cv2 as cv
import os
import signal
from tkinter import Tk, Button, Frame, Label, Text, Scrollbar, END
from PIL import Image, ImageTk

class CameraCalibrationApp:
    def __init__(self):
        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.rows, self.cols = 7, 7
        self.objp = np.zeros((self.rows * self.cols, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.rows, 0:self.cols].T.reshape(-1, 2)
        self.objpoints = []
        self.imgpoints = []
        self.screenshot_folder = 'python/camera/calibration_images'
        self.screenshot_count = 0
        self.stop_camera = False
        self.stop_program_flag = False
        self.cap = None
        self.root = None
        self.label = None
        self.text_widget = None

    def setup_camera(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            self.log_message("Failed to open camera")
            exit()

    def clear_screenshot_folder(self):
        for filename in os.listdir(self.screenshot_folder):
            file_path = os.path.join(self.screenshot_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                self.log_message(f'Failed to delete {file_path}. Reason: {e}')

    def take_screenshot(self):
        ret, frame = self.cap.read()
        if not ret:
            self.log_message("Failed to capture frame")
            return

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_has_chessboard, corners = cv.findChessboardCorners(gray, (self.rows, self.cols), None)

        if frame_has_chessboard:
            screenshot_path = os.path.join(self.screenshot_folder, f'screenshot_{self.screenshot_count}.png')
            cv.imwrite(screenshot_path, frame)
            self.log_message(f'Screenshot {self.screenshot_count + 1} saved.')
            self.screenshot_count += 1

            if self.screenshot_count >= 10:
                self.stop_camera = True
                self.log_message("Camera stopped after 10 screenshots.")
                self.cap.release()

    def stop_program(self):
        self.stop_program_flag = True
        self.root.quit()

    def setup_gui(self):
        self.root = Tk()
        self.root.title("Camera Calibration")

        frame = Frame(self.root)
        frame.pack()

        self.label = Label(frame)
        self.label.pack()

        btn_screenshot = Button(frame, text="Take Screenshot", command=self.take_screenshot, width=30, height=5)
        btn_screenshot.pack()

        text_frame = Frame(self.root)
        text_frame.pack(fill="both", expand=True)
        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        self.text_widget = Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_widget.yview)

        self.root.protocol("WM_DELETE_WINDOW", self.stop_program)

    def log_message(self, message):
        self.text_widget.insert(END, message + "\n")
        self.text_widget.see(END)
        print(message)

    def main_loop(self):
        while not self.stop_program_flag:
            if self.stop_camera:
                self.cap.release()
                break

            ret, frame = self.cap.read()
            if not ret:
                self.log_message("Failed to capture frame")
                break

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (self.rows, self.cols), None)

            if ret:
                cv.drawChessboardCorners(frame, (self.rows, self.cols), corners, ret)

            img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)

            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

            self.root.update_idletasks()
            self.root.update()

    def process_screenshots(self):
        if self.screenshot_count >= 10:
            self.log_message("Processing screenshots for calibration...")
            for i in range(self.screenshot_count):
                img_path = os.path.join(self.screenshot_folder, f'screenshot_{i}.png')
                img = cv.imread(img_path)
                gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                ret, corners = cv.findChessboardCorners(gray, (self.rows, self.cols), None)

                if ret:
                    self.objpoints.append(self.objp)
                    corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                    self.imgpoints.append(corners2)

            if self.objpoints and self.imgpoints:
                self.calibrate_camera(gray.shape[::-1])
            else:
                self.log_message("No calibration data collected.")
        else:
            self.log_message("Not enough screenshots for calibration.")

    def calibrate_camera(self, image_shape):
        self.log_message("Calibrating camera...")
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(self.objpoints, self.imgpoints, image_shape, None, None)
        if ret:
            np.savez('calibration_data.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
            self.log_message("Camera calibration successful.")
            self.log_message(f"Camera matrix:\n{mtx}")
            self.log_message(f"Distortion coefficients:\n{dist}")
        else:
            self.log_message("Failed to calibrate camera")

    def signal_handler(self, sig, frame):
        self.log_message("Interrupt received, stopping...")
        self.stop_program()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        os.makedirs(self.screenshot_folder, exist_ok=True)
        self.clear_screenshot_folder()
        self.setup_camera()
        self.setup_gui()
        self.main_loop()
        self.process_screenshots()
        cv.destroyAllWindows()

if __name__ == "__main__":
    app = CameraCalibrationApp()
    app.run()
