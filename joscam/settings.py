from dataclasses import dataclass


@dataclass
class CameraSettings:
    brightness: float = 0.0
    contrast: float = 1.0
    saturation: float = 1.0
    gamma: float = 1.0
