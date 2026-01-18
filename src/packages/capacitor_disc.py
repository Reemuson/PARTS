# file: src/packages/capacitor_disc.py

"""
@brief	Disc ceramic capacitor package drawing.

Qualifiers:
- @p5, @p7.5, @p10 ...	Lead pitch in mm
- @d7, @d10 ...		    Disc diameter in mm
- @blue, @yellow ...	Body colour (yellow default)
"""

from typing import Optional
from math import atan2, sqrt

from reportlab.lib.colors import HexColor, black
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics

from src.core.geometry import simple_rect, scale_physical
from src.core.markup import draw_markup
from src.core.capacitor_value import capacitor_value_t, tolerance_to_letter
from src.packages.model import resolved_package_t


_DEFAULT_PITCH_MM = 5.0
_DEFAULT_BODY_DIAMETER_MM = 7.0
_DEFAULT_LEAD_DIAMETER_MM = 0.6
_DEFAULT_COLOUR = "yellow"

_YELLOW_BODY = HexColor("#e2ad58")
_YELLOW_INK = HexColor("#c27f49")

_BLUE_BODY = HexColor("#00afd5")
_BLUE_INK = HexColor("#28638c")

_COLOUR_MAP = {
    "yellow": (_YELLOW_BODY, _YELLOW_INK),
    "blue": (_BLUE_BODY, _BLUE_INK),
}


def draw_capacitor_disc(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """@brief		    Draw a disc ceramic capacitor package."""
    pitch_mm = _DEFAULT_PITCH_MM
    colour_name = _DEFAULT_COLOUR

    override_d_mm: Optional[float] = None

    for q in pkg.qualifiers:
        if q.startswith("p"):
            try:
                pitch_mm = float(q[1:])
            except ValueError:
                pass
        elif q.startswith("d"):
            try:
                override_d_mm = float(q[1:])
            except ValueError:
                pass
        elif q in _COLOUR_MAP:
            colour_name = q

    body_d_mm = float(
        override_d_mm
        if override_d_mm is not None
        else pkg.params.get(
            "body_diameter_mm",
            _DEFAULT_BODY_DIAMETER_MM,
        )
    )
    lead_d_mm = float(
        pkg.params.get(
            "lead_diameter_mm",
            _DEFAULT_LEAD_DIAMETER_MM,
        )
    )

    body_col, ink_col = _COLOUR_MAP.get(
        colour_name,
        _COLOUR_MAP[_DEFAULT_COLOUR],
    )

    disc_w, disc_h = scale_physical(rect, body_d_mm, body_d_mm, 2.0)

    scale_x = disc_w / body_d_mm

    pitch = pitch_mm * scale_x
    body_r = disc_w * 0.5
    lead_w = max(0.8, lead_d_mm * scale_x)

    cx = rect.left + (rect.width * 0.50)
    cy = rect.bottom + (rect.height * 0.66)

    lead_bottom = rect.bottom + (rect.height * 0.08)
    lead_extension = rect.height * 0.04
    lead_end = max(lead_bottom - lead_extension, rect.bottom)

    lx = cx - (pitch / 2.0)
    rx = cx + (pitch / 2.0)

    # Lead exits near centre of disc bottom
    exit_dx = body_r * 0.28
    l_exit_x = cx - exit_dx
    r_exit_x = cx + exit_dx

    # --------------------------------------------------
    # Ensure we can always draw a 45° kink (dy == dx)
    # by pushing the disc up if needed.
    # --------------------------------------------------
    min_vertical_room = rect.height * 0.10

    required_kink_drop = max(
        abs(lx - l_exit_x),
        abs(rx - r_exit_x),
    )

    min_cy_for_kink = lead_bottom + min_vertical_room + required_kink_drop + body_r

    max_cy = rect.bottom + rect.height - (body_r * 0.10)
    if cy < min_cy_for_kink:
        cy = min(min_cy_for_kink, max_cy)

    disc_bottom_y = cy - body_r
    exit_y = disc_bottom_y

    # --------------------------------------------------
    # Fixed 45° kink: dy == dx
    # --------------------------------------------------
    l_dx = abs(lx - l_exit_x)
    r_dx = abs(rx - r_exit_x)

    l_kink_end_x = lx
    r_kink_end_x = rx

    l_kink_end_y = exit_y - l_dx
    r_kink_end_y = exit_y - r_dx

    canvas.saveState()

    # --------------------------------------------------
    # Leads + sleeves first
    # --------------------------------------------------
    canvas.setStrokeColorRGB(0.80, 0.80, 0.80)
    canvas.setLineWidth(lead_w)

    _draw_kinked_lead(
        canvas,
        x0=l_exit_x,
        y0=exit_y,
        x1=l_kink_end_x,
        y1=l_kink_end_y,
        x2=lx,
        y2=lead_end,
    )

    _draw_kinked_lead(
        canvas,
        x0=r_exit_x,
        y0=exit_y,
        x1=r_kink_end_x,
        y1=r_kink_end_y,
        x2=rx,
        y2=lead_end,
    )

    _draw_kink_sleeve_half(
        canvas,
        x0=l_exit_x,
        y0=exit_y,
        x1=l_kink_end_x,
        y1=l_kink_end_y,
        fill_col=ink_col,
        body_r=body_r,
        lead_w=lead_w,
    )

    _draw_kink_sleeve_half(
        canvas,
        x0=r_exit_x,
        y0=exit_y,
        x1=r_kink_end_x,
        y1=r_kink_end_y,
        fill_col=ink_col,
        body_r=body_r,
        lead_w=lead_w,
    )

    # --------------------------------------------------
    # Disc last
    # --------------------------------------------------
    canvas.setFillColor(body_col)
    canvas.setStrokeColor(ink_col)
    canvas.setLineWidth(1.0)
    canvas.circle(cx, cy, body_r, stroke=1, fill=1)

    # Marking
    mark = _build_disc_marking(spec)
    if mark:
        font = "Helvetica-Bold"
        font_size = min(body_r * 0.75, rect.height * 0.22)

        ascent = (pdfmetrics.getAscent(font) * font_size) / 1000.0
        descent = (abs(pdfmetrics.getDescent(font)) * font_size) / 1000.0
        text_w = canvas.stringWidth(mark, font, font_size)

        x0 = cx - (text_w / 2.0)
        y0 = cy - ((ascent - descent) / 2.0)

        canvas.setFillColorRGB(0.3, 0.3, 0.3    )
        draw_markup(canvas, x0, y0, mark, font, font_size)

    canvas.restoreState()


def _draw_kinked_lead(
    canvas: Canvas,
    *,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> None:
    """
    @brief	        Draw a lead with a single kink using a path.
    @param canvas	ReportLab canvas.
    @param x0	    Start x (disc exit).
    @param y0	    Start y (disc exit).
    @param x1	    Kink end x.
    @param y1	    Kink end y.
    @param x2	    Vertical end x.
    @param y2	    Vertical end y.
    @return	        None.
    """
    p = canvas.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    p.lineTo(x2, y2)
    canvas.drawPath(p, stroke=1, fill=0)


def _draw_kink_sleeve_half(
    canvas: Canvas,
    *,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    fill_col: object,
    body_r: float,
    lead_w: float,
) -> None:
    """
    @brief	        Draw a sleeve covering the first 50% of the kink segment.
    @param canvas	ReportLab canvas.
    @param x0	    Start x of kink (disc exit).
    @param y0	    Start y of kink (disc exit).
    @param x1	    End x of kink.
    @param y1	    End y of kink.
    @param fill_col	Sleeve colour.
    @param body_r	Disc radius for scale.
    @param lead_w   Lead width for width of sleeve.
    @return	None.
    """
    dx = x1 - x0
    dy = y1 - y0
    seg_len = sqrt((dx * dx) + (dy * dy))
    if seg_len <= 0.0:
        return

    # Unit direction along kink
    ux = dx / seg_len
    uy = dy / seg_len

    # Start sleeve slightly inside disc
    overlap = body_r * 0.10
    sx0 = x0 - (ux * overlap)
    sy0 = y0 - (uy * overlap)

    # Sleeve covers first 50% of kink, plus the overlap
    cover_len = (seg_len * 0.50) + overlap

    # Sleeve centre is half of covered length from its start
    cx = sx0 + (ux * (cover_len * 0.50))
    cy = sy0 + (uy * (cover_len * 0.50))

    angle_deg = atan2(dy, dx) * 180.0 / 3.14

    w = min(body_r * 0.80, cover_len)
    h = lead_w * 1.25
    r = h * 0.35

    canvas.saveState()
    canvas.translate(cx, cy)
    canvas.rotate(angle_deg)
    canvas.setFillColor(fill_col)
    canvas.setStrokeColor(fill_col)
    canvas.setLineWidth(0.6)
    canvas.roundRect(-w * 0.5, -h * 0.5, w, h, r, stroke=1, fill=1)
    canvas.restoreState()


def _build_disc_marking(spec: Optional[object]) -> str:
    """
    @brief	        Build printed marking for a disc capacitor.
    @param  spec	Capacitor spec object.
    @return	        Marking string or empty string.
    """
    if spec is None:
        return ""

    c_value = getattr(spec, "c", None)
    if c_value is None:
        c_value = getattr(spec, "capacitance", None)

    tol = getattr(spec, "tol", None)
    if tol is None:
        tol = getattr(spec, "tolerance", None)

    cv = capacitor_value_t(str(c_value or ""))
    code = cv.get_eia_code()
    if not code:
        return ""

    tol_code = tolerance_to_letter(tol)
    return f"{code}{tol_code}" if tol_code else code
