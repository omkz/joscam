from joscam.effects.basic import (
    brightness,
    contrast,
    exposure,
    gamma,
    highlights_shadows,
    saturation,
    temperature,
    tint,
)
from joscam.settings import CameraSettings


class EffectPipeline:
    def __init__(self, settings: CameraSettings):
        self.settings = settings

    def process(self, frame):
        frame = exposure(
            frame,
            self.settings.exposure,
        )

        frame = highlights_shadows(
            frame,
            self.settings.highlights,
            self.settings.shadows,
        )

        frame = brightness(
            frame,
            self.settings.brightness,
        )

        frame = contrast(
            frame,
            self.settings.contrast,
        )

        frame = temperature(
            frame,
            self.settings.temperature,
        )

        frame = tint(
            frame,
            self.settings.tint,
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