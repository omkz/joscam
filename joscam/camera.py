import cv2


class Camera:
    def __init__(self, device: int = 0):
        self.capture = cv2.VideoCapture(device)

        if not self.capture.isOpened():
            raise RuntimeError(f"Cannot open camera device {device}")

    def read(self):
        ok, frame = self.capture.read()

        if not ok:
            raise RuntimeError("Cannot read frame from camera")

        return frame

    def close(self):
        self.capture.release()
