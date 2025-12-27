# file: src/packages/tht_helpers.py

from math import atan2, cos, degrees, sin, sqrt
from typing import List, Tuple

from reportlab.pdfgen.canvas import Canvas


def parse_pin_config(pc: str) -> list[str]:
    """
    @brief	Split 'g d s' or 'g,d,s' etc into ['G','D','S'].
    @param pc	Pin config string
    @return	List of labels
    """
    return [p.strip() for p in pc.replace(",", " ").split() if p.strip()]


def default_numeric_labels(n: int) -> list[str]:
    """
    @brief	Default numeric labels: ['1','2','3',...].
    @param n	Count
    @return	Labels
    """
    return [str(i + 1) for i in range(n)]


def compute_offsets(pin_count: int, pitch: float) -> list[float]:
    """
    @brief		Return symmetric vertical offsets for leads.
    @param pin_count	Number of pins
    @param pitch	Pin pitch in px
    @return		Offsets in px
    """
    if pin_count == 1:
        return [0.0]
    if pin_count == 2:
        return [-pitch, +pitch]
    return [(i - (pin_count - 1) / 2.0) * pitch for i in range(pin_count)]


def clamp_int(value: int, minimum: int, maximum: int) -> int:
    """
    @brief		Clamp an integer into an inclusive range.
    @param value	Input value
    @param minimum	Minimum value
    @param maximum	Maximum value
    @return		Clamped value
    """
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def clamp_float(value: float, minimum: float, maximum: float) -> float:
    """
    @brief		Clamp a float into an inclusive range, with a minimum and maximum.
    @param value	Input value
    @param minimum	Minimum value
    @param maximum	Maximum value
    @return		Clamped value
    """
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def linspace_angles_deg(count: int, start_deg: float, stop_deg: float) -> List[float]:
    """
    @brief		Generate evenly spaced angles in degrees, inclusive of endpoints.
    @param count	Number of angles
    @param start_deg	Start angle in degrees
    @param stop_deg	Stop angle in degrees
    @return		List of angles
    """
    result: List[float] = []
    count = clamp_int(int(count), 1, 32)

    if count == 1:
        result.append((start_deg + stop_deg) * 0.5)
        return result

    span = stop_deg - start_deg
    step = span / float(count - 1)

    i = 0
    while i < count:
        result.append(start_deg + step * float(i))
        i += 1

    return result


def ring_angles_deg(count: int, start_deg: float = -90.0) -> List[float]:
    """
    @brief		Generate uniformly spaced angles around a full 360° ring.
    @param count	Number of angles
    @param start_deg	Start angle in degrees
    @return		List of angles
    """
    result: List[float] = []
    count = clamp_int(int(count), 1, 32)

    step = 360.0 / float(count)

    i = 0
    while i < count:
        result.append(start_deg + (step * float(i)))
        i += 1

    return result


def draw_pin_with_ring(
    canvas: Canvas,
    *,
    x: float,
    y: float,
    pin_r: float,
    ring_total_diameter_scale: float = 3.0,
    ring_rgb: Tuple[float, float, float] = (0.1, 0.35, 0.9),
    core_rgb: Tuple[float, float, float] = (0.92, 0.92, 0.92),
) -> None:
    """
    @brief				Draw a pin as a filled core circle with a stroked ring.
    @param canvas			ReportLab canvas
    @param x				Pin centre x
    @param y				Pin centre y
    @param pin_r			Core radius in px
    @param ring_total_diameter_scale	Outer ring diameter / core diameter
    @param ring_rgb			Ring colour (r,g,b)
    @param core_rgb			Core colour (r,g,b)
    """
    core_r = clamp_float(pin_r, 0.1, 1.0e9)

    scale = clamp_float(float(ring_total_diameter_scale), 1.05, 10.0)
    ring_outer_r = core_r * scale

    ring_stroke = ring_outer_r - core_r
    ring_stroke = clamp_float(ring_stroke, 0.4, core_r * 6.0)

    ring_draw_r = ring_outer_r - (ring_stroke * 0.5)
    ring_draw_r = clamp_float(ring_draw_r, core_r + 0.05, ring_outer_r)

    canvas.saveState()

    canvas.setStrokeColorRGB(ring_rgb[0], ring_rgb[1], ring_rgb[2])
    canvas.setLineWidth(ring_stroke)
    canvas.circle(x, y, ring_draw_r, stroke=1, fill=0)

    canvas.setFillColorRGB(core_rgb[0], core_rgb[1], core_rgb[2])
    canvas.setLineWidth(max(core_r * 0.15, 0.6))
    canvas.circle(x, y, core_r, stroke=0, fill=1)

    canvas.restoreState()


def draw_radial_pin_label(
    canvas: Canvas,
    *,
    cx: float,
    cy: float,
    pin_x: float,
    pin_y: float,
    label: str,
    font_size: float,
    pad: float,
) -> None:
    """
    @brief		Draw a label placed radially outward from the pin centre.
    @param canvas	ReportLab canvas
    @param cx		Package centre x
    @param cy		Package centre y
    @param pin_x	Pin centre x
    @param pin_y	Pin centre y
    @param label	Label text
    @param font_size	Font size in px
    @param pad		Radial padding in px
    """
    vx = pin_x - cx
    vy = pin_y - cy
    d = sqrt((vx * vx) + (vy * vy))

    if d <= 1.0e-6:
        return

    ux = vx / d
    uy = vy / d

    tx = pin_x + (ux * pad)
    ty = pin_y + (uy * pad)

    canvas.drawCentredString(tx, ty - (font_size * 0.35), label)
