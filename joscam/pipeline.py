from joscam.effects.basic import (
    blur,
    brightness,
    clarity,
    contrast,
    exposure,
    gamma,
    highlights_shadows,
    saturation,
    sharpness,
    skin_smoothing,
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

        frame = skin_smoothing(
            frame,
            self.settings.skin_smoothing,
        )

        frame = blur(
            frame,
            self.settings.blur,
        )

        frame = clarity(
            frame,
            self.settings.clarity,
        )

        frame = sharpness(
            frame,
            self.settings.sharpness,
        )

        return frame