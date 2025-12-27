# file: src/core/geometry.py

from dataclasses import dataclass
from typing import Tuple


@dataclass
class simple_rect:
    """@brief Lightweight rectangle helper for drawing."""

    left: float
    bottom: float
    width: float
    height: float


def rect_centre_scale(rect: simple_rect) -> Tuple[float, float, float]:
    """@brief Return rect centre and nominal size scale."""
    cx = rect.left + rect.width * 0.50
    cy = rect.bottom + rect.height * 0.50
    s = min(rect.width, rect.height) * 0.20
    return cx, cy, s


def scale_physical(
    rect: simple_rect,
    mm_w: float,
    mm_h: float,
    scale_factor: float,
) -> Tuple[float, float]:
    """
    @brief Scale physical mm dimensions into drawing units.

    Scale is applied, then result is clamped to fit inside rect
    without upscaling.
    """
    k = scale_factor

    w = mm_w * k
    h = mm_h * k

    max_w = rect.width
    max_h = rect.height

    f = 1.0
    if w > max_w:
        f = min(f, max_w / w)
    if h > max_h:
        f = min(f, max_h / h)

    if f < 1.0:
        w *= f
        h *= f

    return w, h
