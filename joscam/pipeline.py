from joscam.effects.basic import (
    brightness,
    contrast,
    gamma,
    saturation,
)
from joscam.settings import CameraSettings


class EffectPipeline:
    def __init__(self, settings: CameraSettings):
        self.settings = settings

    def process(self, frame):
        frame = brightness(
            frame,
            self.settings.brightness,
        )

        frame = contrast(
            frame,
            self.settings.contrast,
        )

        frame = saturation(
            frame,
            self.settings.saturation,
        )

        frame = gamma(
            frame,
            self.settings.gamma,
        )

        return frame
