
# file: src/symbols/diode_symbols.py

from typing import Callable, Dict

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, rect_centre_scale

from src.core.drawing_utils import draw_arrow, tri_path, draw_cathode_bar


# ------------------------------------------------------------
# Variant bodies
# ------------------------------------------------------------


def _variant_zener(canvas: Canvas, cx: float, cy: float, s: float) -> None:
    wing_x = 0.50 * s
    wing_y = 0.30 * s
    bar_x = cx + s

    for sign in (+1, -1):
        p = canvas.beginPath()
        p.moveTo(bar_x, cy)
        p.lineTo(bar_x, cy + sign * s)
        p.lineTo(bar_x - sign * wing_x, cy + sign * s + sign * wing_y)
        canvas.drawPath(p)


def _variant_schottky(canvas: Canvas, cx: float, cy: float, s: float) -> None:
    hook = 0.60 * s
    drop = 0.30 * s

    p = canvas.beginPath()
    p.moveTo(cx + s, cy)
    p.lineTo(cx + s, cy + s)
    p.lineTo(cx + s + hook, cy + s)
    p.lineTo(cx + s + hook, cy + s - drop)
    canvas.drawPath(p)

    p = canvas.beginPath()
    p.moveTo(cx + s, cy)
    p.lineTo(cx + s, cy - s)
    p.lineTo(cx + s - hook, cy - s)
    p.lineTo(cx + s - hook, cy - s + drop)
    canvas.drawPath(p)


def _variant_tunnel(canvas: Canvas, cx: float, cy: float, s: float) -> None:
    hook = 0.60 * s
    for sign in (+1, -1):
        p = canvas.beginPath()
        p.moveTo(cx + s, cy)
        p.lineTo(cx + s, cy + sign * s)
        p.lineTo(cx + s - hook, cy + sign * s)
        canvas.drawPath(p)


# ------------------------------------------------------------
# Generic diode body
# ------------------------------------------------------------


def _draw_diode_body(
    canvas: Canvas,
    cx: float,
    cy: float,
    s: float,
    *,
    mirrored: bool,
    cathode: bool,
    variant,
) -> None:
    canvas.setStrokeColor(black)
    canvas.setLineWidth(1.4)
    canvas.setLineCap(0)
    canvas.setLineJoin(0)

    tri = tri_path(canvas, cx, cy, s, mirrored)
    canvas.drawPath(tri, stroke=0, fill=1)

    if cathode:
        draw_cathode_bar(canvas, cx, cy, s, mirrored)

    if variant is not None:
        variant(canvas, cx, cy, s)


# ------------------------------------------------------------
# Symbol templates
# ------------------------------------------------------------


def _draw_symbol_template(
    canvas: Canvas,
    rect: simple_rect,
    *,
    draw_leads: bool = True,
    triangle: bool = True,
    cathode: bool = True,
    variant=None,
    extras=None,
    mirrored: bool = False,
) -> None:
    cx, cy, s = rect_centre_scale(rect)

    if draw_leads:
        lead = 2.5 * s
        canvas.setLineWidth(1.4)
        canvas.setStrokeColor(black)
        canvas.line(cx - lead, cy, cx - s, cy)
        canvas.line(cx + s, cy, cx + lead, cy)

    if triangle:
        _draw_diode_body(
            canvas,
            cx,
            cy,
            s,
            mirrored=mirrored,
            cathode=cathode,
            variant=variant,
        )

    if extras is not None:
        extras(canvas, cx, cy, s)


# ------------------------------------------------------------
# Concrete symbol drawers
# ------------------------------------------------------------


def _draw_symbol_standard(canvas: Canvas, rect: simple_rect) -> None:
    _draw_symbol_template(canvas, rect)


def _draw_symbol_schottky(canvas: Canvas, rect: simple_rect) -> None:
    _draw_symbol_template(canvas, rect, cathode=False, variant=_variant_schottky)


def _draw_symbol_zener(canvas: Canvas, rect: simple_rect) -> None:
    _draw_symbol_template(canvas, rect, variant=_variant_zener)


def _draw_symbol_led(canvas: Canvas, rect: simple_rect) -> None:
    cx, cy, s = rect_centre_scale(rect)
    _draw_symbol_template(canvas, rect)
    draw_arrow(canvas, cx, cy + s, cx + 0.7 * s, cy + 1.5 * s, s)
    draw_arrow(canvas, cx - 0.7 * s, cy + s, cx, cy + 1.5 * s, s)


def _draw_symbol_photodiode(canvas: Canvas, rect: simple_rect) -> None:
    cx, cy, s = rect_centre_scale(rect)
    _draw_symbol_template(canvas, rect)
    draw_arrow(canvas, cx + 0.7 * s, cy + 1.5 * s, cx, cy + s, s)
    draw_arrow(canvas, cx, cy + 1.5 * s, cx - 0.7 * s, cy + s, s)


def _draw_symbol_tvs(canvas: Canvas, rect: simple_rect) -> None:
    cx, cy, s = rect_centre_scale(rect)
    lead = 2.5 * s

    _draw_diode_body(
        canvas, cx - s, cy, s, mirrored=False, cathode=True, variant=_variant_zener
    )

    _draw_diode_body(canvas, cx + s, cy, s, mirrored=True, cathode=True, variant=None)

    canvas.setLineWidth(1.4)
    canvas.line(cx - lead, cy, cx - 2 * s, cy)
    canvas.line(cx + 2 * s, cy, cx + lead, cy)


def _draw_symbol_tunnel(canvas: Canvas, rect: simple_rect) -> None:
    _draw_symbol_template(canvas, rect, cathode=False, variant=_variant_tunnel)


def _draw_symbol_varicap(canvas: Canvas, rect: simple_rect) -> None:
    def extras(c: Canvas, cx: float, cy: float, s: float) -> None:
        lead_width = 1.4
        plate_width = 1.6
        lead = 2.5 * s

        c.setLineWidth(lead_width)
        c.line(cx - lead, cy, cx - s, cy)

        c.setLineWidth(plate_width)
        x1 = cx + s
        c.line(x1, cy + s, x1, cy - s)

        x2 = x1 + 0.5 * s
        c.line(x2, cy + s, x2, cy - s)

        c.setLineWidth(lead_width)
        c.line(x2, cy, cx + lead, cy)

    _draw_symbol_template(canvas, rect, draw_leads=False, cathode=False, extras=extras)


# ------------------------------------------------------------
# Registry exported for routing
# ------------------------------------------------------------

DIODE_DRAWERS: Dict[str, Callable[[Canvas, simple_rect], None]] = {
    "standard": _draw_symbol_standard,
    "diode": _draw_symbol_standard,
    "rectifier": _draw_symbol_standard,
    "zener": _draw_symbol_zener,
    "schottky": _draw_symbol_schottky,
    "led": _draw_symbol_led,
    "photodiode": _draw_symbol_photodiode,
    "photo": _draw_symbol_photodiode,
    "tvs-bi": _draw_symbol_tvs,
    "tvs-uni": _draw_symbol_zener,
    "tvs": _draw_symbol_tvs,
    "tunnel": _draw_symbol_tunnel,
    "varicap": _draw_symbol_varicap,
    "varactor": _draw_symbol_varicap,
}
