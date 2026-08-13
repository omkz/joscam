from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Look:
    category: str
    temperature: float = 0.0
    tint: float = 0.0
    saturation: float = 1.0
    contrast: float = 1.0
    gamma: float = 1.0
    lift: float = 0.0
    gain: float = 1.0
    blue_scale: float = 1.0
    shadow_tint: tuple = (0.0, 0.0, 0.0)
    highlight_tint: tuple = (0.0, 0.0, 0.0)
    protect_highlights: bool = False


CATEGORIES = {
    "Social": [
        "Clean",
        "Warm Glow",
        "Cool Clean",
        "Soft Pastel",
        "Golden",
        "Vintage",
    ],
    "Cinematic": [
        "Northern Cold",
        "Medieval",
        "Royal Warm",
        "Dragonstone",
        "Night Battle",
        "Epic Fantasy",
    ],
}


LOOKS = {
    "Clean": Look(
        category="Social",
        saturation=1.05,
        contrast=1.05,
        gain=1.03,
    ),
    "Warm Glow": Look(
        category="Social",
        temperature=0.08,
        gain=1.05,
        saturation=1.05,
        contrast=0.96,
        highlight_tint=(-5.0, 5.0, 15.0),
    ),
    "Cool Clean": Look(
        category="Social",
        temperature=-0.06,
        contrast=1.08,
    ),
    "Soft Pastel": Look(
        category="Social",
        temperature=0.04,
        contrast=0.88,
        lift=18.0,
        saturation=0.85,
    ),
    "Golden": Look(
        category="Social",
        temperature=0.12,
        saturation=1.10,
        highlight_tint=(-10.0, 5.0, 20.0),
    ),
    "Vintage": Look(
        category="Social",
        temperature=0.06,
        saturation=0.75,
        lift=10.0,
        contrast=0.92,
        blue_scale=0.90,
        highlight_tint=(-10.0, 5.0, 15.0),
    ),
    "Northern Cold": Look(
        category="Cinematic",
        temperature=-0.12,
        tint=-0.02,
        saturation=0.75,
        contrast=1.15,
        shadow_tint=(15.0, 5.0, -10.0),
    ),
    "Medieval": Look(
        category="Cinematic",
        temperature=0.05,
        saturation=0.70,
        contrast=1.05,
        gain=0.95,
        shadow_tint=(-5.0, 5.0, 0.0),
        highlight_tint=(-5.0, 3.0, 3.0),
    ),
    "Royal Warm": Look(
        category="Cinematic",
        temperature=0.10,
        saturation=1.05,
        contrast=1.08,
        gain=0.92,
        highlight_tint=(-8.0, 5.0, 15.0),
    ),
    "Dragonstone": Look(
        category="Cinematic",
        temperature=-0.10,
        tint=-0.02,
        saturation=0.65,
        contrast=1.18,
        highlight_tint=(10.0, 2.0, -5.0),
    ),
    "Night Battle": Look(
        category="Cinematic",
        temperature=-0.15,
        saturation=0.70,
        contrast=1.10,
        gain=0.75,
        lift=-5.0,
        shadow_tint=(10.0, 0.0, -5.0),
        protect_highlights=True,
    ),
    "Epic Fantasy": Look(
        category="Cinematic",
        temperature=0.03,
        saturation=0.85,
        contrast=1.12,
        shadow_tint=(8.0, 0.0, -5.0),
        highlight_tint=(-8.0, 5.0, 12.0),
    ),
}


def _apply_temperature_tint(img, temperature, tint):
    if temperature:
        img[:, :, 2] *= 1.0 + temperature
        img[:, :, 0] *= 1.0 - temperature

    if tint:
        img[:, :, 1] *= 1.0 - tint
        img[:, :, 0] *= 1.0 + tint * 0.35
        img[:, :, 2] *= 1.0 + tint * 0.35

    return img


def _apply_tone_tint(img, shadow_tint, highlight_tint):
    if shadow_tint == (0.0, 0.0, 0.0) and highlight_tint == (0.0, 0.0, 0.0):
        return img

    luminance = (
        img[:, :, 0] * 0.114
        + img[:, :, 1] * 0.587
        + img[:, :, 2] * 0.299
    ) / 255.0

    shadow_mask = np.clip((0.5 - luminance) * 2, 0, 1)
    highlight_mask = np.clip((luminance - 0.5) * 2, 0, 1)

    for channel in range(3):
        img[:, :, channel] += shadow_tint[channel] * shadow_mask
        img[:, :, channel] += highlight_tint[channel] * highlight_mask

    return img


def _protect_highlights(frame):
    img = frame.astype(np.float32) / 255.0

    knee = 0.8
    over = img > knee

    img[over] = knee + (img[over] - knee) * 0.5

    return np.clip(img * 255, 0, 255).astype(np.uint8)


def _grade(frame, look: Look):
    img = frame.astype(np.float32)

    img = _apply_temperature_tint(img, look.temperature, look.tint)

    if look.blue_scale != 1.0:
        img[:, :, 0] *= look.blue_scale

    if look.lift != 0.0 or look.gain != 1.0:
        img = img * look.gain + look.lift

    img = _apply_tone_tint(img, look.shadow_tint, look.highlight_tint)

    img = np.clip(img, 0, 255).astype(np.uint8)

    if look.saturation != 1.0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= look.saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    if look.contrast != 1.0:
        img = img.astype(np.float32)
        img = (img - 127.5) * look.contrast + 127.5
        img = np.clip(img, 0, 255).astype(np.uint8)

    if look.gamma != 1.0:
        value = max(look.gamma, 0.01)

        table = np.array([
            ((i / 255.0) ** (1.0 / value)) * 255
            for i in range(256)
        ]).astype(np.uint8)

        img = cv2.LUT(img, table)

    if look.protect_highlights:
        img = _protect_highlights(img)

    return img


def apply_filter(frame, name, intensity):
    if not name or name == "None" or intensity <= 0:
        return frame

    look = LOOKS.get(name)

    if look is None:
        return frame

    intensity = min(max(intensity, 0.0), 1.0)

    graded = _grade(frame, look)

    blended = (
        frame.astype(np.float32) * (1 - intensity)
        + graded.astype(np.float32) * intensity
    )

    return np.clip(blended, 0, 255).astype(np.uint8)
