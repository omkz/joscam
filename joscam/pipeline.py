from joscam.effects.basic import (
    blur,
    brightness,
    clarity,
    contrast,
    exposure,
    fade,
    gamma,
    grain,
    highlights_shadows,
    saturation,
    sharpness,
    skin_smoothing,
    temperature,
    tint,
    vignette,
)
from joscam.filters import apply_filter
from joscam.settings import CameraSettings


class EffectPipeline:
    def __init__(self, settings: CameraSettings):
        self.settings = settings

        # Filter/look layer. Kept separate from CameraSettings:
        # it is a look applied on top of a preset, not part of it.
        self.filter_name = "None"
        self.filter_intensity = 1.0

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

        frame = apply_filter(
            frame,
            self.filter_name,
            self.filter_intensity,
        )

        frame = fade(
            frame,
            self.settings.fade,
        )

        frame = vignette(
            frame,
            self.settings.vignette,
        )

        frame = grain(
            frame,
            self.settings.grain,
        )

        return frame