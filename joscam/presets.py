from joscam.settings import CameraSettings


PRESETS = {
    "Neutral": CameraSettings(
        brightness=0,
        contrast=1.00,
        saturation=1.00,
        gamma=1.00,
    ),

    "Natural": CameraSettings(
        brightness=4,
        contrast=1.05,
        saturation=1.02,
        gamma=1.03,
    ),

    "Soft": CameraSettings(
        brightness=7,
        contrast=0.96,
        saturation=0.95,
        gamma=1.06,
    ),

    "Cinematic": CameraSettings(
        brightness=2,
        contrast=1.12,
        saturation=0.88,
        gamma=0.98,
    ),

    "Moody": CameraSettings(
        brightness=-5,
        contrast=1.18,
        saturation=0.78,
        gamma=0.92,
    ),
}
