from functools import lru_cache

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

def exposure(frame, value: float):
    img = frame.astype(np.float32)
    img *= 2.0 ** value

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)


def temperature(frame, value: float):
    if value == 0:
        return frame

    img = frame.astype(np.float32)

    # BGR
    img[:, :, 2] *= 1.0 + value
    img[:, :, 0] *= 1.0 - value

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)


def tint(frame, value: float):
    if value == 0:
        return frame

    img = frame.astype(np.float32)

    # + = magenta
    # - = green
    img[:, :, 1] *= 1.0 - value
    img[:, :, 0] *= 1.0 + value * 0.35
    img[:, :, 2] *= 1.0 + value * 0.35

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)


def highlights_shadows(
    frame,
    highlights: float,
    shadows: float,
):
    img = frame.astype(np.float32) / 255.0

    luminance = (
        img[:, :, 0] * 0.114
        + img[:, :, 1] * 0.587
        + img[:, :, 2] * 0.299
    )

    shadow_mask = np.clip(
        (0.5 - luminance) * 2,
        0,
        1,
    )

    highlight_mask = np.clip(
        (luminance - 0.5) * 2,
        0,
        1,
    )

    img += (
        shadows
        * shadow_mask[:, :, None]
        * 0.30
    )

    img += (
        highlights
        * highlight_mask[:, :, None]
        * 0.30
    )

    return np.clip(
        img * 255,
        0,
        255,
    ).astype(np.uint8)


def blur(frame, value: float):
    if value <= 0:
        return frame

    sigma = value * 10.0

    return cv2.GaussianBlur(
        frame,
        (0, 0),
        sigmaX=sigma,
    )


def skin_smoothing(frame, value: float):
    if value <= 0:
        return frame

    smoothed = cv2.bilateralFilter(
        frame,
        d=9,
        sigmaColor=75,
        sigmaSpace=75,
    )

    return cv2.addWeighted(
        smoothed,
        value,
        frame,
        1 - value,
        0,
    )


def clarity(frame, value: float):
    if value == 0:
        return frame

    blurred = cv2.GaussianBlur(
        frame,
        (0, 0),
        sigmaX=20,
    )

    return cv2.addWeighted(
        frame,
        1 + value,
        blurred,
        -value,
        0,
    )


def sharpness(frame, value: float):
    if value <= 0:
        return frame

    blurred = cv2.GaussianBlur(
        frame,
        (0, 0),
        sigmaX=3,
    )

    return cv2.addWeighted(
        frame,
        1 + value,
        blurred,
        -value,
        0,
    )


def fade(frame, value: float):
    if value <= 0:
        return frame

    img = frame.astype(np.float32)

    lift = 40.0 * value
    gain = 1.0 - 0.3 * value

    img = img * gain + lift

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)


@lru_cache(maxsize=4)
def _vignette_mask(height, width):
    y, x = np.indices(
        (height, width),
        dtype=np.float32,
    )

    center_y = (height - 1) / 2.0
    center_x = (width - 1) / 2.0

    ny = (y - center_y) / center_y
    nx = (x - center_x) / center_x

    distance_sq = nx ** 2 + ny ** 2

    return np.exp(-distance_sq / 1.2)


def vignette(frame, value: float):
    if value <= 0:
        return frame

    height, width = frame.shape[:2]

    mask = _vignette_mask(height, width)

    strength = mask * value + (1 - value)

    img = frame.astype(np.float32) * strength[:, :, None]

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)


def grain(frame, value: float):
    if value <= 0:
        return frame

    height, width = frame.shape[:2]

    noise = np.random.normal(
        loc=0.0,
        scale=value * 200.0,
        size=(height, width),
    ).astype(np.float32)

    img = frame.astype(np.float32) + noise[:, :, None]

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)
