# file: label_layout.py
from dataclasses import dataclass
from typing import Optional

from reportlab.lib.units import inch


@dataclass
class label_rect_t:
    """@brief Simple rectangle container used for label layout."""

    left: float
    bottom: float
    width: float
    height: float


@dataclass
class label_layout_t:
    """@brief Unified layout split for a single sticker cell."""

    usable: label_rect_t
    text: Optional[label_rect_t]
    symbol: Optional[label_rect_t]


def compute_label_layout(
    rect,
    symbol_fraction: Optional[float] = None,
) -> label_layout_t:
    """@brief Compute a unified layout for a label."""
    inner_left = rect.left + 0.05 * inch
    inner_width = rect.width - 0.10 * inch

    usable = label_rect_t(
        left=inner_left,
        bottom=rect.bottom,
        width=inner_width,
        height=rect.height,
    )

    if symbol_fraction is None:
        return label_layout_t(usable=usable, text=None, symbol=None)

    symbol_width = usable.width * symbol_fraction
    symbol_left = usable.left + usable.width - symbol_width

    symbol = label_rect_t(
        left=symbol_left,
        bottom=usable.bottom,
        width=symbol_width,
        height=usable.height,
    )

    text = label_rect_t(
        left=usable.left,
        bottom=usable.bottom,
        width=usable.width - symbol_width,
        height=usable.height,
    )

    return label_layout_t(usable=usable, text=text, symbol=symbol)
