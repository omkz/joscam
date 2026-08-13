import logging
import platform

import cv2

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        device: int = 0,
        width: int = None,
        height: int = None,
        fps: int = None,
    ):
        backend = (
            cv2.CAP_V4L2
            if platform.system() == "Linux"
            else cv2.CAP_ANY
        )

        self.capture = cv2.VideoCapture(device, backend)

        if not self.capture.isOpened():
            raise RuntimeError(f"Cannot open camera device {device}")

        if width:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)

        if height:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if fps:
            self.capture.set(cv2.CAP_PROP_FPS, fps)

        # The camera driver may not honor the requested values, so
        # read back what was actually negotiated.
        self.actual_width = int(
            self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        )
        self.actual_height = int(
            self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
        self.actual_fps = self.capture.get(cv2.CAP_PROP_FPS)

        logger.info(
            "Camera %s opened: requested %sx%s@%sfps, actual %dx%d@%.2ffps",
            device,
            width,
            height,
            fps,
            self.actual_width,
            self.actual_height,
            self.actual_fps,
        )

    def read(self):
        ok, frame = self.capture.read()

        if not ok:
            raise RuntimeError("Cannot read frame from camera")

        return frame

    def close(self):
        self.capture.release()
