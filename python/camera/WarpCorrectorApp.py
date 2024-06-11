import numpy as np
import cv2 as cv
import time

class WarpCorrectorApp:
    def __init__(self):
        self.calibration_data = np.load('calibration_data.npz')
        self.cam_matrix = self.calibration_data['mtx']
        self.dist = self.calibration_data['dist']

        self.camera_origin_x = 0
        self.camera_origin_y = 0
        self.scale_factor = 1

        self.cap = None
        self.new_camera_materix = None
        self.region_of_interest = None

    def transform_coordinates(self, camera_x, camera_y):
        translated_x = camera_x - self.camera_origin_x
        translated_y = camera_y - self.camera_origin_y

        robot_x = translated_x * self.scale_factor
        robot_y = translated_y * self.scale_factor

        return robot_x, robot_y

    def setup_camera(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            exit()

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture image")
            self.cap.release()
            exit()

        h, w = frame.shape[:2]
        self.new_camera_materix, self.region_of_interest = cv.getOptimalNewCameraMatrix(self.cam_matrix, self.dist, (w, h), 1, (w, h))

    def capture_and_process_frame(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            dst = cv.undistort(frame, self.cam_matrix, self.dist, None, self.new_camera_materix)
            gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (7, 7), None)

            if ret:
                self.display_countdown(dst)
                self.process_chessboard_corners(dst, gray, corners)
                break
         
            print("Chessboard corners not found")
            cv.imshow('Chessboard', dst)

            if cv.waitKey(1) == 27:  # ESC key
                break

        self.cap.release()
        cv.destroyAllWindows()

    def display_countdown(self, frame):
        for i in range(3, 0, -1):
            countdown_frame = frame.copy()
            cv.putText(countdown_frame, str(i), (frame.shape[1] // 2, frame.shape[0] // 2), 
                       cv.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10, cv.LINE_AA)
            cv.imshow('Countdown', countdown_frame)
            cv.waitKey(1000)
        cv.destroyWindow('Countdown')

    def process_chessboard_corners(self, dst, gray, corners):
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                   (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        cv.drawChessboardCorners(dst, (7, 7), corners2, True)
        cv.imshow('Chessboard', dst)
        cv.waitKey(500)

        objp = np.zeros((7*7, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

        ret, rvec, tvec = cv.solvePnP(objp, corners2, self.cam_matrix, self.dist)

        point_3d = np.array([(3, 3, 0)], dtype=np.float32)
        point_2d, _ = cv.projectPoints(point_3d, rvec, tvec, self.cam_matrix, self.dist)
        point_2d = point_2d[0][0]

        print("Projected point on image: ", point_2d)

        robot_x, robot_y = self.transform_coordinates(point_2d[0], point_2d[1])
        print("Robot coordinates: ", (robot_x, robot_y))

        cv.circle(dst, (int(point_2d[0]), int(point_2d[1])), 5, (0, 0, 255), -1)
        cv.imshow('Projected Point', dst)
        cv.waitKey(0)
        cv.destroyAllWindows()

    def run(self):
        self.setup_camera()
        self.capture_and_process_frame()

if __name__ == "__main__":
    app = WarpCorrectorApp()
    app.run()
