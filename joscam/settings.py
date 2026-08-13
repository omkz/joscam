from dataclasses import dataclass


@dataclass
class CameraSettings:
    brightness: float = 0.0
    contrast: float = 1.0
    saturation: float = 1.0
    gamma: float = 1.0

    exposure: float = 0.0
    temperature: float = 0.0
    tint: float = 0.0
    highlights: float = 0.0
    shadows: float = 0.0

    blur: float = 0.0
    skin_smoothing: float = 0.0
    clarity: float = 0.0
    sharpness: float = 0.0