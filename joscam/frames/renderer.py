from functools import lru_cache

import numpy as np

from joscam.frames.styles import BUILTIN_STYLES


def _edge_alpha(distance, offset, feather):
    """1.0 up to `offset`, fading smoothly to 0.0 over `feather` pixels."""
    if feather <= 0:
        return (distance <= offset).astype(np.float32)

    t = np.clip((distance - offset) / feather, 0.0, 1.0)

    return 1.0 - t * t * (3.0 - 2.0 * t)


@lru_cache(maxsize=8)
def _build_masks(
    width,
    height,
    shape,
    size,
    position_x,
    position_y,
    feather,
    border_width,
):
    """Geometric alpha masks for the current shape/size/position/feather.

    Returns (inner_alpha, border_band, background_alpha), each an (H, W)
    float32 array in [0, 1] that sums to exactly 1 at every pixel.
    """
    yy, xx = np.indices((height, width), dtype=np.float32)

    cx = width / 2.0 + position_x * width
    cy = height / 2.0 + position_y * height

    if shape == "Circle":
        radius = max(size * (min(width, height) / 2.0), 1.0)

        ratio = np.sqrt(
            ((xx - cx) / radius) ** 2
            + ((yy - cy) / radius) ** 2
        )
        distance = (ratio - 1.0) * radius

    elif shape == "Oval":
        radius_x = max(size * (width / 2.0), 1.0)
        radius_y = max(size * (height / 2.0), 1.0)

        ratio = np.sqrt(
            ((xx - cx) / radius_x) ** 2
            + ((yy - cy) / radius_y) ** 2
        )
        distance = (ratio - 1.0) * radius_x

    else:  # Rounded Rectangle
        half_w = max(size * (width / 2.0), 1.0)
        half_h = max(size * (height / 2.0), 1.0)
        corner_radius = 0.2 * min(half_w, half_h)

        qx = np.abs(xx - cx) - (half_w - corner_radius)
        qy = np.abs(yy - cy) - (half_h - corner_radius)

        outside = np.sqrt(
            np.clip(qx, 0, None) ** 2
            + np.clip(qy, 0, None) ** 2
        )
        inside = np.minimum(np.maximum(qx, qy), 0.0)

        distance = outside + inside - corner_radius

    inner_alpha = _edge_alpha(distance, 0.0, feather)
    outer_alpha = _edge_alpha(distance, border_width, feather)

    border_band = outer_alpha - inner_alpha
    background_alpha = 1.0 - outer_alpha

    return inner_alpha, border_band, background_alpha


@lru_cache(maxsize=4)
def _build_gradient_background(width, height, style_name):
    style = BUILTIN_STYLES[style_name]

    yy, xx = np.indices((height, width), dtype=np.float32)
    cx, cy = width / 2.0, height / 2.0

    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_dist = max(np.sqrt(cx ** 2 + cy ** 2), 1.0)
    t = np.clip(dist / max_dist, 0.0, 1.0)

    result = np.zeros((height, width, 3), dtype=np.float32)
    stops = style.gradient_stops

    for (pos0, color0), (pos1, color1) in zip(stops, stops[1:]):
        span = max(pos1 - pos0, 1e-6)
        local_t = np.clip((t - pos0) / span, 0.0, 1.0)
        segment = (t >= pos0) & (t <= pos1)

        for channel in range(3):
            blended = color0[channel] + (color1[channel] - color0[channel]) * local_t
            result[:, :, channel] = np.where(
                segment,
                blended,
                result[:, :, channel],
            )

    return result.astype(np.uint8)


def render_frame(frame, settings):
    if settings.style == "None":
        return frame

    height, width = frame.shape[:2]

    inner_alpha, border_band, background_alpha = _build_masks(
        width,
        height,
        settings.shape,
        settings.size,
        settings.position_x,
        settings.position_y,
        settings.feather,
        settings.border_width,
    )

    if settings.style == "Custom":
        border_color = settings.border_color
        outside_color = settings.outside_color
        background = None
    else:
        style = BUILTIN_STYLES[settings.style]
        border_color = style.border_color
        outside_color = None
        background = _build_gradient_background(
            width,
            height,
            settings.style,
        )

    result = frame.astype(np.float32) * inner_alpha[:, :, None]

    if background is not None:
        result += background.astype(np.float32) * background_alpha[:, :, None]
    else:
        for channel in range(3):
            result[:, :, channel] += outside_color[channel] * background_alpha

    if settings.border_width > 0:
        for channel in range(3):
            result[:, :, channel] += border_color[channel] * border_band

    return np.clip(result, 0, 255).astype(np.uint8)
