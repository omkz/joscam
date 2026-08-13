from dataclasses import dataclass, field


SHAPES = ["Circle", "Oval", "Rounded Rectangle"]

STYLE_NAMES = ["None", "Retro 70s", "Retro 90s", "Custom"]


@dataclass
class FrameSettings:
    """User-facing frame configuration. Lives on EffectPipeline, kept
    entirely separate from CameraSettings and the filter/look layer.
    """

    style: str = "None"
    shape: str = "Circle"
    size: float = 0.85
    feather: float = 10.0
    border_width: float = 6.0
    position_x: float = 0.0
    position_y: float = 0.0

    # Only used when style == "Custom". Colors are BGR to match the
    # frames coming out of the rest of the pipeline.
    outside_color: tuple = (60, 60, 60)
    border_color: tuple = (255, 255, 255)


@dataclass
class BuiltinStyle:
    # Gradient stops from the center outward: (position 0-1, BGR color).
    gradient_stops: list = field(default_factory=list)
    border_color: tuple = (0, 0, 0)


BUILTIN_STYLES = {
    "Retro 70s": BuiltinStyle(
        gradient_stops=[
            (0.0, (192, 225, 240)),  # warm cream / beige
            (0.4, (23, 160, 212)),   # mustard yellow
            (0.7, (42, 80, 181)),    # burnt orange
            (1.0, (35, 39, 62)),     # dark brown
        ],
        border_color=(35, 39, 62),
    ),
    "Retro 90s": BuiltinStyle(
        gradient_stops=[
            (0.0, (22, 22, 22)),     # near-black
            (0.35, (138, 75, 91)),   # muted purple
            (0.7, (179, 166, 34)),   # cyan accent
            (1.0, (140, 59, 179)),   # magenta accent
        ],
        border_color=(179, 166, 34),
    ),
}
