"""Conservative, local face retouching using OpenCV's bundled detector.

This is cosmetic smoothing, not generative age transformation. Detection is
performed on every enabled frame: a missing face never leaves a stale mask.
"""

import cv2
import numpy as np


class FaceBeauty:
    def __init__(self):
        self.detector = None

    def _faces(self, frame):
        if self.detector is None:
            self.detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            if self.detector.empty():
                raise RuntimeError("OpenCV face detector could not be loaded")
        height, width = frame.shape[:2]
        scale = min(1.0, 480.0 / width)
        small = cv2.resize(frame, (max(1, round(width * scale)),
                                   max(1, round(height * scale))))
        gray = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
        faces = self.detector.detectMultiScale(
            gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40)
        )
        return [tuple(round(int(v) / scale) for v in face) for face in faces]

    @staticmethod
    def _mask(roi):
        height, width = roi.shape[:2]
        yy, xx = np.mgrid[:height, :width].astype(np.float32)
        xx = (xx + 0.5) / width
        yy = (yy + 0.5) / height
        distance = ((xx - 0.5) / 0.43) ** 2 + ((yy - 0.51) / 0.49) ** 2
        mask = np.clip((1.0 - distance) * 5.0, 0, 1)
        # Broad exclusions protect eyes/eyebrows and mouth without claiming
        # landmark precision. Profile faces require a future landmark tracker.
        for cx, cy, rx, ry in ((0.30, 0.39, 0.24, 0.14),
                               (0.70, 0.39, 0.24, 0.14),
                               (0.50, 0.77, 0.30, 0.13)):
            d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
            mask *= np.clip((d - 0.7) * 3.0, 0, 1)
        # Preserve dark and strongly textured detail (including facial hair).
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
        detail = np.abs(gray - cv2.GaussianBlur(gray, (0, 0), 2))
        mask *= np.clip((gray - 15) / 35, 0, 1)
        mask *= 1.0 - 0.85 * np.clip(detail / 20, 0, 1)
        return mask[:, :, None]

    def process(self, frame, smoothing=0.0, light=0.0):
        smoothing = float(np.clip(smoothing, 0, 1))
        light = float(np.clip(light, 0, 1))
        if smoothing == 0 and light == 0:
            return frame
        output = frame.copy()
        height, width = frame.shape[:2]
        for x, y, w, h in self._faces(frame):
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(width, x + w), min(height, y + h)
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            roi = frame[y0:y1, x0:x1]
            mask = self._mask(roi)
            original = roi.astype(np.float32)
            target = original.copy()
            if smoothing:
                smooth = cv2.bilateralFilter(roi, 9, 35, 9).astype(np.float32)
                target += (smooth - original) * smoothing * 0.85
            if light:
                # Lift midtones while preserving highlights and skin hue.
                target += light * 0.18 * target * (1 - target / 255)
            output[y0:y1, x0:x1] = np.clip(
                original + (target - original) * mask, 0, 255
            ).astype(np.uint8)
        return output
