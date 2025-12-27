# file: src/packages/to205.py

from math import cos, radians, sin

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    clamp_float,
    clamp_int,
    default_numeric_labels,
    draw_pin_with_ring,
    draw_radial_pin_label,
    parse_pin_config,
    ring_angles_deg,
)


def _draw_tab_under_body_show_outside(
    canvas: Canvas,
    *,
    cx: float,
    cy: float,
    body_r: float,
    tab_w: float,
    tab_h: float,
    angle_deg: float,
    fill_rgb: tuple[float, float, float],
) -> None:
    """
    @brief		Draw a rotated rectangular tab first, then later the body is
                        drawn over it so only the outside portion remains visible.
    @note		This draws the full tab (unclipped). The caller must draw the
                        body afterwards to mask the inside portion.
    @param canvas	ReportLab canvas
    @param cx		Body centre x
    @param cy		Body centre y
    @param body_r	Body radius in px
    @param tab_w	Tab width in px
    @param tab_h	Tab height in px
    @param angle_deg	Rotation angle in degrees
    @param fill_rgb	Fill colour RGB tuple
    """
    tab_cx = cx - (body_r * 0.70)
    tab_cy = cy - (body_r * 0.70)

    canvas.saveState()

    canvas.translate(tab_cx, tab_cy)
    canvas.rotate(angle_deg)

    canvas.setFillColorRGB(fill_rgb[0], fill_rgb[1], fill_rgb[2])
    canvas.rect(
        -tab_w * 0.5,
        -tab_h * 0.5,
        tab_w,
        tab_h,
        stroke=0,
        fill=1,
    )

    canvas.restoreState()


def _to205_pin_angles_deg(*, pin_count: int) -> list[float]:
    """
    @brief		Return pin angles in degrees for TO-205.
    @note		3-pin is placed as if it were a 4-pin with the bottom missing:
                        pin 1 left, pin 2 top, pin 3 right.
    @param pin_count	Pin count (3..8)
    @return		List of angles in degrees
    """
    if pin_count == 3:
        return [180.0, 90.0, 0.0]

    return ring_angles_deg(pin_count, start_deg=-90.0)


def draw_to205_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    spec: object | None = None,
) -> None:
    """
    @brief		Draw a TO-205 style round can package underside view.
    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pin_count	Pin count (3..8)
    @param spec		Resolved package params and optional pin metadata
    """
    pin_count = clamp_int(int(pin_count), 3, 8)

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    elif spec is not None and getattr(spec, "pin_labels", None):
        final_labels = getattr(spec, "pin_labels")
    else:
        final_labels = default_numeric_labels(pin_count)

    body_d_mm = float(getattr(spec, "body_d_mm", 9.4))
    tab_h_mm = float(getattr(spec, "tab_h_mm", 1))
    tab_w_mm = float(getattr(spec, "tab_w_mm", 1.8))

    pin_diameter_mm = float(getattr(spec, "pin_diameter_mm", 0.74))
    pin_ring_scale = float(getattr(spec, "pin_ring_scale", 2.0))

    pin_ring_radius_mm = float(getattr(spec, "pin_ring_radius_mm", 2.54))

    body_pin_index = getattr(spec, "pin_connected_to_body", None)
    if body_pin_index is None:
        body_pin_index = pin_count
    body_pin_index = clamp_int(int(body_pin_index), 1, pin_count)

    phys_w = body_d_mm
    phys_h = body_d_mm
    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_r = min(draw_w, draw_h) * 0.5

    tab_w = (tab_w_mm / body_d_mm) * (body_r * 2.0)
    tab_h = (tab_h_mm / body_d_mm) * (body_r * 2.0)

    body_fill_rgb = (0.78, 0.77, 0.76)
    body_stroke_rgb = (0.68, 0.67, 0.66)

    _draw_tab_under_body_show_outside(
        canvas,
        cx=cx,
        cy=cy,
        body_r=body_r,
        tab_w=tab_w,
        tab_h=tab_h,
        angle_deg=45.0,
        fill_rgb=body_stroke_rgb,
    )

    canvas.setFillColorRGB(body_fill_rgb[0], body_fill_rgb[1], body_fill_rgb[2])
    canvas.setStrokeColorRGB(body_stroke_rgb[0], body_stroke_rgb[1], body_stroke_rgb[2])
    canvas.setLineWidth(1.0)
    canvas.circle(cx, cy, body_r, stroke=1, fill=1)

    pin_r = (pin_diameter_mm / body_d_mm) * (body_r * 2.0) * 0.5
    pin_r = clamp_float(pin_r, body_r * 0.035, body_r * 0.11)

    pin_ring_r = (pin_ring_radius_mm / body_d_mm) * (body_r * 2.0)
    pin_ring_r = clamp_float(pin_ring_r, body_r * 0.35, body_r * 0.70)

    angles = _to205_pin_angles_deg(pin_count=pin_count)

    font_size = rect.height * 0.20
    font_size = clamp_float(font_size, rect.height * 0.08, rect.height * 0.16)

    canvas.setFont("Helvetica", font_size)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    radial_pad = max(pin_r * 4.0, font_size * 1.1)

    i = 0
    while i < pin_count:
        a = radians(angles[i])
        px = cx + pin_ring_r * cos(a)
        py = cy + pin_ring_r * sin(a)

        pin_index_1based = i + 1
        if pin_index_1based == body_pin_index:
            ring_rgb = (0.55, 0.54, 0.53)
        else:
            ring_rgb = (0.28, 0.24, 0.21)

        draw_pin_with_ring(
            canvas,
            x=px,
            y=py,
            pin_r=pin_r,
            ring_total_diameter_scale=pin_ring_scale,
            ring_rgb=ring_rgb,
        )

        if i < len(final_labels):
            label = str(final_labels[i]).upper()
            draw_radial_pin_label(
                canvas,
                cx=cx,
                cy=cy,
                pin_x=px,
                pin_y=py,
                label=label,
                font_size=font_size,
                pad=radial_pad,
            )

        i += 1

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
