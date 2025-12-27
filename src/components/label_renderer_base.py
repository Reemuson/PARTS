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


# ---------------------------------------------------------------------------
# Centre guideline
# ---------------------------------------------------------------------------


def draw_center_line(canvas: Canvas, rect) -> None:
    """
    @brief Draw a faint horizontal centre line for grid alignment.

    @param canvas PDF canvas to draw onto.
    @param rect Rectangle describing the label bounds.
    """
    canvas.setStrokeColor(black, 0.25)
    canvas.setLineWidth(0.7)

    y = rect.bottom + rect.height * 0.50

    canvas.line(
        rect.left,
        y,
        rect.left + rect.width,
        y,
    )
