import cv2
import numpy as np


def brightness(frame, value: float):
    return cv2.convertScaleAbs(frame, alpha=1.0, beta=value)


def contrast(frame, value: float):
    frame = frame.astype(np.float32)

    frame = (frame - 127.5) * value + 127.5

    return np.clip(frame, 0, 255).astype(np.uint8)


def saturation(frame, value: float):
    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV,
    ).astype(np.float32)

    hsv[:, :, 1] *= value
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)

    return cv2.cvtColor(
        hsv.astype(np.uint8),
        cv2.COLOR_HSV2BGR,
    )


def gamma(frame, value: float):
    value = max(value, 0.01)

    table = np.array([
        ((i / 255.0) ** (1.0 / value)) * 255
        for i in range(256)
    ]).astype(np.uint8)

    return cv2.LUT(frame, table)
