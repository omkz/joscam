from functools import lru_cache

import cv2
import numpy as np


def brightness(frame, value: float):
    if value == 0:
        return frame

    return cv2.convertScaleAbs(frame, alpha=1.0, beta=value)


def contrast(frame, value: float):
    if value == 1.0:
        return frame

    frame = frame.astype(np.float32)

    frame = (frame - 127.5) * value + 127.5

    return np.clip(frame, 0, 255).astype(np.uint8)


def saturation(frame, value: float):
    if value == 1.0:
        return frame

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


@lru_cache(maxsize=32)
def _gamma_table(value: float):
    value = max(value, 0.01)

    return np.array([
        ((i / 255.0) ** (1.0 / value)) * 255
        for i in range(256)
    ]).astype(np.uint8)


def gamma(frame, value: float):
    if value == 1.0:
        return frame

    return cv2.LUT(frame, _gamma_table(value))


def exposure(frame, value: float):
    if value == 0:
        return frame

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
    if highlights == 0 and shadows == 0:
        return frame

    img = frame.astype(np.float32)

    # BGR2GRAY uses the same 0.299/0.587/0.114 weights, computed in C++
    # (much faster than a manual per-channel numpy reduction).
    luminance = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY,
    ).astype(np.float32)

    shadow_mask = np.clip(
        (127.5 - luminance) * (2 / 255.0),
        0,
        1,
    )

    highlight_mask = np.clip(
        (luminance - 127.5) * (2 / 255.0),
        0,
        1,
    )

    img += (
        (shadows * 0.30 * 255)
        * shadow_mask[:, :, None]
    )

    img += (
        (highlights * 0.30 * 255)
        * highlight_mask[:, :, None]
    )

    return np.clip(
        img,
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

    height, width = frame.shape[:2]

    # Bilateral filtering is expensive at full resolution. Run it on a
    # quarter-area version and upscale, then blend against the original.
    small = cv2.resize(
        frame,
        (width // 2, height // 2),
        interpolation=cv2.INTER_LINEAR,
    )

    smoothed_small = cv2.bilateralFilter(
        small,
        d=9,
        sigmaColor=75,
        sigmaSpace=75,
    )

    smoothed = cv2.resize(
        smoothed_small,
        (width, height),
        interpolation=cv2.INTER_LINEAR,
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

    height, width = frame.shape[:2]

    # The low-frequency blur only needs to be smooth, not sharp, so it
    # can be computed at quarter resolution and upscaled much faster
    # than a large-sigma blur over the full frame.
    small = cv2.resize(
        frame,
        (width // 4, height // 4),
        interpolation=cv2.INTER_LINEAR,
    )

    blurred_small = cv2.GaussianBlur(
        small,
        (0, 0),
        sigmaX=5,
    )

    blurred = cv2.resize(
        blurred_small,
        (width, height),
        interpolation=cv2.INTER_LINEAR,
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


@lru_cache(maxsize=4)
def _noise_buffer(height, width):
    return np.empty((height, width), dtype=np.float32)


def grain(frame, value: float):
    if value <= 0:
        return frame

    height, width = frame.shape[:2]

    # Reuse a scratch buffer per frame size and fill it via OpenCV's
    # RNG, which is noticeably faster than numpy's for this size.
    noise = _noise_buffer(height, width)
    cv2.randn(noise, 0.0, value * 200.0)

    img = frame.astype(np.float32) + noise[:, :, None]

    return np.clip(
        img,
        0,
        255,
    ).astype(np.uint8)
