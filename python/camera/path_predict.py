import cv2 as cv
import numpy as np

# Video capture van de camera
cap = cv.VideoCapture(0)

# Parameters voor Shi-Tomasi-corner-detectie
feature_params = dict(maxCorners=100,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)

# Parameters voor Lucas-Kanade optische stroom
lk_params = dict(winSize=(15, 15),
                maxLevel=2,
                criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# Kleur voor sporen tekenen
color = np.random.randint(0, 255, (100, 3))

def track_and_predict():
    # Lees het eerste frame en converteer naar grijswaarden
    ret, old_frame = cap.read()
    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)

    # Detecteer hoekpunten in het eerste frame
    p0 = cv.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    # Creëer een masker voor sporen
    mask = np.zeros_like(old_frame)

    # Lus door de frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Bereken Optical Flow met Lucas-Kanade-methode
        p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        # Selecteer goede punten
        good_new = p1[st == 1]
        good_old = p0[st == 1]

        # Teken de tracks
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel().astype(int)
            c, d = old.ravel().astype(int)
            mask = cv.line(mask, (a, b), (c, d), color[i].tolist(), 2)
            frame = cv.circle(frame, (a, b), 5, color[i].tolist(), -1)

        # Voeg het optische stroommasker toe aan het frame
        img = cv.add(frame, mask)

        # Toon het resultaat
        cv.imshow('Frame', img)

        # Update de oude frame en oude punten
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)

        # Wacht op ESC om te stoppen
        if cv.waitKey(30) & 0xff == 27:
            break

    # Release capture en sluit vensters
    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    track_and_predict()
