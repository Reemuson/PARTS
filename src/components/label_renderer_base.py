# file: src/components/label_renderer_base.py

"""
@brief Shared helpers for all label renderers.
Provides unified margins, centre-line drawing and standard font sizes.
"""

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black
from reportlab.lib.units import inch


# ---------------------------------------------------------------------------
# Standard font roles used by all label types
# ---------------------------------------------------------------------------

label_fonts = {
    "title": 0.125 * inch,
    "meta": 0.075 * inch,
    "spec": 0.075 * inch,
    "smd": 0.070 * inch,
}


# ---------------------------------------------------------------------------
# Margin application
# ---------------------------------------------------------------------------


def apply_standard_margins(rect) -> None:
    """
    @brief Apply unified horizontal margins to all label rectangles.

    @param rect Sticker rectangle instance to modify.
    """
    rect.width -= 0.10 * inch
    rect.left += 0.05 * inch