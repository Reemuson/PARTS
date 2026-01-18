# file: src/symbols/capacitor.py

"""
@brief	Capacitor schematic symbols.
"""

from math import pi

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black

from src.core.geometry import simple_rect


def _draw_capacitor_standard(
    canvas: Canvas,
    rect: simple_rect,
    _unused: str | None = None,
) -> None:
    """
    @brief	Draw a non-polarised capacitor symbol.
    @param canvas	Target canvas.
    @param rect	Symbol bounding box.
    @param _unused	Unused subtype hint.
    @return	None.
    """
    canvas.setStrokeColor(black)
    canvas.setFillColor(black)

    cx = rect.left + (rect.width * 0.50)
    cy = rect.bottom + (rect.height * 0.50)

    gap = min(rect.width, rect.height) * 0.12
    plate_h = rect.height * 0.55
    plate_w = rect.width * 0.02
    lead = rect.width * 0.30

    left_plate_x = cx - (gap / 2.0)
    right_plate_x = cx + (gap / 2.0)

    y0 = cy - (plate_h / 2.0)
    y1 = cy + (plate_h / 2.0)

    canvas.setLineWidth(1.2)
    canvas.line(left_plate_x, y0, left_plate_x, y1)
    canvas.line(right_plate_x, y0, right_plate_x, y1)

    canvas.line(left_plate_x - lead, cy, left_plate_x, cy)
    canvas.line(right_plate_x, cy, right_plate_x + lead, cy)


def _draw_capacitor_polarised(
    canvas: Canvas,
    rect: simple_rect,
    _unused: str | None = None,
) -> None:
    """
    @brief	Draw a polarised capacitor symbol.
    @param canvas	Target canvas.
    @param rect	Symbol bounding box.
    @param _unused	Unused subtype hint.
    @return	None.
    """
    canvas.setStrokeColor(black)
    canvas.setFillColor(black)

    cx = rect.left + (rect.width * 0.50)
    cy = rect.bottom + (rect.height * 0.50)

    gap = min(rect.width, rect.height) * 0.12
    plate_h = rect.height * 0.55
    lead = rect.width * 0.30

    left_plate_x = cx - (gap / 2.0)
    right_plate_x = cx + (gap / 2.0)

    y0 = cy - (plate_h / 2.0)
    y1 = cy + (plate_h / 2.0)

    canvas.setLineWidth(1.2)

    # Negative plate (straight)
    canvas.line(left_plate_x, y0, left_plate_x, y1)

    # Positive plate (curved approximation via multiple short segments)
    arc_r = plate_h * 0.55
    steps = 16
    for i in range(steps):
        a0 = (-pi / 2.0) + (pi * (i / steps))
        a1 = (-pi / 2.0) + (pi * ((i + 1) / steps))
        x0 = right_plate_x + (arc_r * 0.25) * (1.0 - (abs(a0) / (pi / 2.0)))
        y0s = cy + arc_r * (a0 / (pi / 2.0))
        x1 = right_plate_x + (arc_r * 0.25) * (1.0 - (abs(a1) / (pi / 2.0)))
        y1s = cy + arc_r * (a1 / (pi / 2.0))
        canvas.line(x0, y0s, x1, y1s)

    # Leads
    canvas.line(left_plate_x - lead, cy, left_plate_x, cy)
    canvas.line(right_plate_x, cy, right_plate_x + lead, cy)

    # Plus mark on the positive side
    plus_x = right_plate_x + (lead * 0.65)
    plus_y = cy + (plate_h * 0.35)
    plus_s = min(rect.width, rect.height) * 0.08
    canvas.setLineWidth(1.0)
    canvas.line(plus_x - plus_s, plus_y, plus_x + plus_s, plus_y)
    canvas.line(plus_x, plus_y - plus_s, plus_x, plus_y + plus_s)


def _is_polarised_subtype(subtype: str) -> bool:
    """
    @brief	Check whether a capacitor subtype is polarised by default.
    @param subtype	Subtype string.
    @return	True if polarised.
    """
    st = subtype.strip().lower()
    return st in ("electrolytic", "tantalum", "polymer", "supercap")


def _draw_capacitor_auto(
    canvas: Canvas,
    rect: simple_rect,
    subtype: str | None,
) -> None:
    """
    @brief	Draw capacitor symbol with polarisation inferred from subtype.
    @param canvas	Target canvas.
    @param rect	Symbol bounding box.
    @param subtype	Subtype string.
    @return	None.
    """
    if subtype and _is_polarised_subtype(subtype):
        _draw_capacitor_polarised(canvas, rect, None)
    else:
        _draw_capacitor_standard(canvas, rect, None)


CAPACITOR_DRAWERS = {
    "standard": _draw_capacitor_standard,
    "ceramic": _draw_capacitor_standard,
    "film": _draw_capacitor_standard,
    "mica": _draw_capacitor_standard,
    "paper": _draw_capacitor_standard,
    "variable": _draw_capacitor_standard,
    "trimmer": _draw_capacitor_standard,
    "electrolytic": _draw_capacitor_polarised,
    "tantalum": _draw_capacitor_polarised,
    "polymer": _draw_capacitor_polarised,
    "supercap": _draw_capacitor_polarised,
    "default": _draw_capacitor_auto,
}
