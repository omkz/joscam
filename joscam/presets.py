from joscam.settings import CameraSettings


PRESETS = {
    "Neutral": CameraSettings(
        brightness=0,
        contrast=1.00,
        saturation=1.00,
        gamma=1.00,
        skin_smoothing=0.00,
        blur=0.00,
        clarity=0.00,
        sharpness=0.00,
    ),

    "Natural": CameraSettings(
        brightness=4,
        contrast=1.05,
        saturation=1.02,
        gamma=1.03,
        skin_smoothing=0.15,
        blur=0.00,
        clarity=0.03,
        sharpness=0.06,
    ),

    "Soft": CameraSettings(
        brightness=7,
        contrast=0.96,
        saturation=0.95,
        gamma=1.06,
        skin_smoothing=0.30,
        blur=0.03,
        clarity=-0.05,
        sharpness=0.03,
    ),

    "Cinematic": CameraSettings(
        brightness=2,
        contrast=1.12,
        saturation=0.88,
        gamma=0.98,
        skin_smoothing=0.12,
        blur=0.00,
        clarity=0.08,
        sharpness=0.08,
    ),

    "Moody": CameraSettings(
        brightness=-5,
        contrast=1.18,
        saturation=0.78,
        gamma=0.92,
        skin_smoothing=0.08,
        blur=0.00,
        clarity=0.12,
        sharpness=0.10,
    ),
}
