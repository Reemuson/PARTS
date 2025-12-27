# file: src/symbols/transistor.py

from typing import Dict, Callable

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect
from src.core.drawing_utils import draw_arrow


# ----------------------------------------------------------------------
# Common helpers
# ----------------------------------------------------------------------


def _circle_frame(rect: simple_rect) -> tuple[float, float, float]:
    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5
    r = min(rect.width, rect.height) * 0.40
    return cx, cy, r


# ----------------------------------------------------------------------
# BJT (NPN / PNP) – IEC with circle
# ----------------------------------------------------------------------


def _draw_bjt(
    canvas: Canvas, rect: simple_rect, is_pnp: bool, is_darlington: bool = False
) -> None:
    canvas.setStrokeColor(black)
    canvas.setFillColor(black)
    cx, cy, r = _circle_frame(rect)

    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    lead_ext = r * 0.40

    # Base vertical bar inside circle
    bar_x = cx - r * 0.25
    bar_y0 = cy - r * 0.70
    bar_y1 = cy + r * 0.70
    canvas.setLineWidth(2.0)
    canvas.line(bar_x, bar_y0, bar_x, bar_y1)
    canvas.setLineWidth(1.2)

    # Base external lead (left)
    bx_ext = cx - r - lead_ext
    canvas.line(bx_ext, cy, bar_x, cy)

    # Collector diagonal + lead (top)
    c_in_x = bar_x
    c_in_y = cy + r * 0.30
    c_out_x = cx + r * 0.45
    c_out_y = cy + r * 0.90
    canvas.line(c_in_x, c_in_y, c_out_x, c_out_y)
    canvas.line(c_out_x, c_out_y, c_out_x, cy + r + lead_ext * 0.3)

    # Darlington second collector diagonal (IEC cue)
    if is_darlington:
        offset = -r * 0.3
        canvas.line(
            c_in_x,
            c_in_y + offset,
            c_out_x,
            c_out_y + offset,
        )
        canvas.line(c_out_x, c_out_y + offset * 1.1, c_out_x, cy + r + lead_ext * 0.3)

    # Emitter diagonal + lead (bottom)
    e_in_x = bar_x
    e_in_y = cy - r * 0.30
    e_out_x = cx + r * 0.45
    e_out_y = cy - r * 0.90
    canvas.line(e_in_x, e_in_y, e_out_x, e_out_y)
    canvas.line(e_out_x, e_out_y, e_out_x, cy - r - lead_ext * 0.3)

    # Arrow on emitter diagonal
    t = 0.55
    ax1 = e_in_x + (e_out_x - e_in_x) * (t - 0.20)
    ay1 = e_in_y + (e_out_y - e_in_y) * (t - 0.20)
    ax2 = e_in_x + (e_out_x - e_in_x) * (t + 0.20)
    ay2 = e_in_y + (e_out_y - e_in_y) * (t + 0.20)
    size = r * 0.7

    if is_pnp:
        # Arrow into emitter (towards bar)
        draw_arrow(canvas, ax2, ay2, ax1, ay1, size)
    else:
        # Arrow out of emitter (away from bar)
        draw_arrow(canvas, ax1, ay1, ax2, ay2, size)


def draw_bjt_npn(canvas: Canvas, rect: simple_rect) -> None:
    _draw_bjt(canvas, rect, is_pnp=False)


def draw_bjt_pnp(canvas: Canvas, rect: simple_rect) -> None:
    _draw_bjt(canvas, rect, is_pnp=True)


def draw_bjt_darlington_npn(canvas: Canvas, rect: simple_rect) -> None:
    _draw_bjt(canvas, rect, is_pnp=False, is_darlington=True)


def draw_bjt_darlington_pnp(canvas: Canvas, rect: simple_rect) -> None:
    _draw_bjt(canvas, rect, is_pnp=True, is_darlington=True)


# ----------------------------------------------------------------------
# MOSFET (N/P, enhancement and depletion) – IEC with circle
# ----------------------------------------------------------------------


def _draw_mosfet(
    canvas: Canvas,
    rect: simple_rect,
    *,
    is_p_channel: bool,
    is_depletion: bool,
) -> None:
    # ------------------------------
    # Frame circle
    # ------------------------------
    cx, cy, r = _circle_frame(rect)
    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    # Geometry
    gate_x = cx - r * 0.55
    ch_x = gate_x + r * 0.25
    y0 = cy - r * 0.70
    y1 = cy + r * 0.70

    # ------------------------------
    # Gate
    # ------------------------------
    canvas.line(gate_x, y0, gate_x, y1)

    # Gate lead
    g_ext_x = gate_x - r * 0.60
    gate_y = y0 + 0.60
    canvas.line(g_ext_x, gate_y, gate_x, gate_y)

    # ------------------------------
    # Channel (IEC)
    # ------------------------------
    gap = r * 0.20  # half-gap size
    gate_h = y1 - y0
    channel_h = (gate_h - gap * 2.0) / 3.0

    canvas.setLineWidth(1.2)

    if is_depletion:
        # Solid channel
        canvas.line(ch_x, y0, ch_x, y1)
    else:
        # Enhancement: solid–gap–solid-gap-solid
        canvas.line(ch_x, y1, ch_x, y1 - channel_h)
        canvas.line(ch_x, y1 - channel_h - gap, ch_x, y1 - 2.0 * channel_h - gap)
        canvas.line(ch_x, y0 + channel_h, ch_x, y0)

    # ------------------------------
    # Source and Drain leads
    # IEC: P-channel is vertically flipped
    # ------------------------------
    lead_out = r * 0.40
    canvas.setLineWidth(1.2)

    # Drain (top)
    canvas.line(ch_x, y1 - channel_h * 0.50, ch_x + r * 0.75, y1 - channel_h * 0.50)
    canvas.line(
        ch_x + r * 0.75, y1 - channel_h * 0.50 - 0.6, ch_x + r * 0.75, y1 + lead_out
    )

    # Source (bottom)
    canvas.line(ch_x, y0 + channel_h * 0.50, ch_x + r * 0.75, y0 + channel_h * 0.50)
    canvas.line(
        ch_x + r * 0.75,
        y0 + gate_h * 0.50 + 0.5,
        ch_x + r * 0.75,
        y0 + channel_h * 0.50,
    )
    canvas.line(ch_x + r * 0.75, y0 + channel_h * 0.50, ch_x + r * 0.75, y0 - lead_out)

    # ------------------------------
    # Arrow on source (IEC)
    # ------------------------------
    arrow_y = y0 + gate_h * 0.50
    arrow_x = ch_x + r * 0.70
    arrow_dx = r * 0.60
    arrow_sz = r * 0.50

    if is_p_channel:
        # Arrow OUT of the device
        draw_arrow(
            canvas, arrow_x - arrow_dx - 0.6, arrow_y, arrow_x, arrow_y, arrow_sz
        )
    else:
        # Arrow INTO the device
        draw_arrow(canvas, arrow_x, arrow_y, arrow_x - arrow_dx, arrow_y, arrow_sz)


def draw_mosfet_n_enh(canvas: Canvas, rect: simple_rect) -> None:
    _draw_mosfet(canvas, rect, is_p_channel=False, is_depletion=False)


def draw_mosfet_p_enh(canvas: Canvas, rect: simple_rect) -> None:
    _draw_mosfet(canvas, rect, is_p_channel=True, is_depletion=False)


def draw_mosfet_n_dep(canvas: Canvas, rect: simple_rect) -> None:
    _draw_mosfet(canvas, rect, is_p_channel=False, is_depletion=True)


def draw_mosfet_p_dep(canvas: Canvas, rect: simple_rect) -> None:
    _draw_mosfet(canvas, rect, is_p_channel=True, is_depletion=True)


# ----------------------------------------------------------------------
# JFET (simple IEC variant with circle)
# ----------------------------------------------------------------------


def _draw_jfet(canvas: Canvas, rect: simple_rect, is_p_channel: bool) -> None:
    # ------------------------------
    # Frame circle
    # ------------------------------
    cx, cy, r = _circle_frame(rect)
    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    # Geometry
    gate_x = cx - r * 0.25
    y0 = cy - r * 0.70
    y1 = cy + r * 0.70

    # ------------------------------
    # Source and Drain leads
    # IEC: P-channel is vertically flipped
    # ------------------------------

    gap = r * 0.20  # half-gap size
    gate_h = y1 - y0
    channel_h = (gate_h - gap * 2.0) / 3.0
    lead_out = r * 0.40
    canvas.setLineWidth(1.2)

    # Drain (top)
    canvas.line(gate_x, y1 - channel_h * 0.50, gate_x + r * 0.75, y1 - channel_h * 0.50)
    canvas.line(
        gate_x + r * 0.75, y1 - channel_h * 0.50 - 0.6, gate_x + r * 0.75, y1 + lead_out
    )

    # Source (bottom)
    canvas.line(gate_x, y0 + channel_h * 0.50, gate_x + r * 0.75, y0 + channel_h * 0.50)
    canvas.line(
        gate_x + r * 0.75, y0 + channel_h * 0.50 + 0.6, gate_x + r * 0.75, y0 - lead_out
    )

    # ------------------------------
    # Gate
    # ------------------------------
    canvas.setLineWidth(2.0)
    canvas.line(gate_x, y0, gate_x, y1)
    canvas.setLineWidth(1.2)

    arrow_y = y0 + channel_h * 0.50
    arrow_x = gate_x
    arrow_dx = r
    arrow_sz = r * 0.50

    if is_p_channel:
        # Arrow OUT of the device
        draw_arrow(canvas, arrow_x, arrow_y, arrow_x - arrow_dx, arrow_y, arrow_sz)
    else:
        # Arrow INTO the device
        draw_arrow(
            canvas, arrow_x - arrow_dx, arrow_y, arrow_x - 1.2, arrow_y, arrow_sz
        )


def draw_jfet_n(canvas: Canvas, rect: simple_rect) -> None:
    _draw_jfet(canvas, rect, is_p_channel=False)


def draw_jfet_p(canvas: Canvas, rect: simple_rect) -> None:
    _draw_jfet(canvas, rect, is_p_channel=True)


# ----------------------------------------------------------------------
# IGBT – approximate IEC symbol inside circle
# ----------------------------------------------------------------------


def _draw_igbt(canvas: Canvas, rect: simple_rect, is_p_channel: bool) -> None:
    canvas.setStrokeColor(black)
    canvas.setFillColor(black)
    cx, cy, r = _circle_frame(rect)

    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    lead_ext = r * 0.30

    # Gate vertical bar inside circle
    bar_x = cx - r * 0.30
    bar_x0 = bar_x - r * 0.25
    bar_y0 = cy - r * 0.70
    bar_y1 = cy + r * 0.70
    canvas.line(bar_x0, bar_y0, bar_x0, bar_y1)
    canvas.line(bar_x, bar_y0, bar_x, bar_y1)

    # Gate external lead (left)
    bx_ext = cx - r - lead_ext
    gate_y = bar_y0 + 0.60
    canvas.line(bx_ext, gate_y, bar_x0, gate_y)

    # Collector diagonal + lead (top)
    c_in_x = bar_x
    c_in_y = cy + r * 0.30
    c_out_x = cx + r * 0.45
    c_out_y = cy + r * 0.90
    canvas.line(c_in_x, c_in_y, c_out_x, c_out_y)
    canvas.line(c_out_x, c_out_y, c_out_x, cy + r + lead_ext * 0.3)

    # Emitter diagonal + lead (bottom)
    e_in_x = bar_x
    e_in_y = cy - r * 0.30
    e_out_x = cx + r * 0.45
    e_out_y = cy - r * 0.90
    canvas.line(e_in_x, e_in_y, e_out_x, e_out_y)
    canvas.line(e_out_x, e_out_y, e_out_x, cy - r - lead_ext * 0.3)

    # Arrow on emitter diagonal
    t = 0.55
    ax1 = e_in_x + (e_out_x - e_in_x) * (t - 0.20)
    ay1 = e_in_y + (e_out_y - e_in_y) * (t - 0.20)
    ax2 = e_in_x + (e_out_x - e_in_x) * (t + 0.20)
    ay2 = e_in_y + (e_out_y - e_in_y) * (t + 0.20)
    size = r * 0.7

    if is_p_channel:
        # Arrow into emitter (towards bar)
        draw_arrow(canvas, ax2, ay2, ax1, ay1, size)
    else:
        # Arrow out of emitter (away from bar)
        draw_arrow(canvas, ax1, ay1, ax2, ay2, size)


def draw_igbt_n(canvas: Canvas, rect: simple_rect) -> None:
    _draw_igbt(canvas, rect, is_p_channel=False)


def draw_igbt_p(canvas: Canvas, rect: simple_rect) -> None:
    _draw_igbt(canvas, rect, is_p_channel=True)


# ----------------------------------------------------------------------
# SCR / TRIAC (simplified IEC-style, inside circle)
# ----------------------------------------------------------------------


def draw_scr(canvas: Canvas, rect: simple_rect) -> None:
    cx, cy, r = _circle_frame(rect)

    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    lead_ext = r * 0.60

    # Main A-K path (vertical)
    ax = cx
    ay_top = cy + r * 0.70
    ay_bot = cy - r * 0.70
    canvas.line(ax, ay_top, ax, ay_bot)

    # External anode / cathode
    canvas.line(ax, ay_top, ax, cy + r + lead_ext * 0.3)
    canvas.line(ax, ay_bot, ax, cy - r - lead_ext * 0.3)

    # Gate from left into lower half
    gx0 = cx - r - lead_ext * 0.2
    gy = cy - r * 0.25
    canvas.line(gx0, gy, ax - r * 0.15, gy)


def draw_triac(canvas: Canvas, rect: simple_rect) -> None:
    cx, cy, r = _circle_frame(rect)

    canvas.setLineWidth(1.2)
    canvas.circle(cx, cy, r, stroke=1, fill=0)

    lead_ext = r * 0.60

    # Two opposing vertical paths for MT1 / MT2
    x1 = cx - r * 0.20
    x2 = cx + r * 0.20
    y_top = cy + r * 0.70
    y_bot = cy - r * 0.70

    canvas.line(x1, y_top, x1, y_bot)
    canvas.line(x2, y_top, x2, y_bot)

    # External MT2 (top), MT1 (bottom)
    canvas.line(x2, y_top, x2, cy + r + lead_ext * 0.3)
    canvas.line(x1, y_bot, x1, cy - r - lead_ext * 0.3)

    # Gate from left into middle
    gx0 = cx - r - lead_ext * 0.2
    gy = cy
    canvas.line(gx0, gy, x1, gy)


# ----------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------

TRANSISTOR_DRAWERS: Dict[str, Callable[[Canvas, simple_rect], None]] = {
    # BJTs
    "npn": draw_bjt_npn,
    "pnp": draw_bjt_pnp,
    "bjt_npn": draw_bjt_npn,
    "bjt_pnp": draw_bjt_pnp,
    "darlington_npn": draw_bjt_darlington_npn,
    "darlington_pnp": draw_bjt_darlington_pnp,
    # MOSFETs
    "nmos": draw_mosfet_n_enh,
    "pmos": draw_mosfet_p_enh,
    "nmos_enh": draw_mosfet_n_enh,
    "pmos_enh": draw_mosfet_p_enh,
    "nmos_dep": draw_mosfet_n_dep,
    "pmos_dep": draw_mosfet_p_dep,
    # JFETs
    "jfet_n": draw_jfet_n,
    "jfet_p": draw_jfet_p,
    # IGBT
    "igbt_n": draw_igbt_n,
    "igbt_p": draw_igbt_p,
    # SCR / TRIAC
    "scr": draw_scr,
    "triac": draw_triac,
    # Fallback
    "default": draw_bjt_npn,
}
