# file: src/packages/to264.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
    compute_offsets,
)


def _draw_internal_scallop(
    canvas,
    *,
    cx,
    edge_y,
    r,
    body_x,
    body_w,
    cy,
):
    canvas.saveState()

    path = canvas.beginPath()
    path.circle(cx, edge_y, r)
    canvas.clipPath(path, stroke=0, fill=0)

    if edge_y >= cy:
        clip_y = edge_y - r
    else:
        clip_y = edge_y

    canvas.rect(
        body_x,
        clip_y,
        body_w,
        r,
        fill=1,
        stroke=0,
    )

    canvas.restoreState()


def draw_to264_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    spec: object | None = None,
) -> None:
    """@brief Draw a TO-264 package (2, 3 or 5 pins) in side view."""
    if pin_count not in (2, 3, 5):
        pin_count = 3

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    elif spec is not None and getattr(spec, "pin_labels", None):
        final_labels = getattr(spec, "pin_labels")
    else:
        final_labels = default_numeric_labels(pin_count)

    body_mm = float(getattr(spec, "body_mm", 20.0))
    lead_mm = float(getattr(spec, "lead_mm", 20.5))
    height_mm = float(getattr(spec, "height_mm", 26.0))

    hole_d_mm = float(getattr(spec, "hole_d_mm", 3.4))
    scallop_d_mm = float(getattr(spec, "scallop_d_mm", 4.5))
    scallop_x_mm = float(getattr(spec, "scallop_y_mm", 6.2))

    total_x_mm = height_mm + lead_mm
    phys_w = total_x_mm
    phys_h = body_mm

    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    label_margin_fraction = 0.15
    cx = rect.left + (rect.width * (1.0 - label_margin_fraction)) * 0.5
    cy = rect.bottom + rect.height * 0.50

    x0 = cx - draw_w * 0.5
    y0 = cy - draw_h * 0.5

    body_w = draw_w * (height_mm / total_x_mm)
    lead_w = draw_w * (lead_mm / total_x_mm)

    body_x = x0

    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.rect(body_x, y0, body_w, draw_h, fill=1, stroke=0)

    hole_r = (hole_d_mm / body_mm) * draw_h * 0.5
    scallop_r = (scallop_d_mm / body_mm) * draw_h * 0.5
    scallop_dx = (scallop_x_mm / height_mm) * body_w

    canvas.setFillColorRGB(1.0, 1.0, 1.0)

    canvas.circle(
        body_x + scallop_dx,
        cy,
        hole_r,
        fill=1,
        stroke=0,
    )

    top_edge_y = y0 + draw_h
    bot_edge_y = y0

    canvas.setFillColorRGB(0.25, 0.25, 0.25)

    for edge_y in (top_edge_y, bot_edge_y):
        _draw_internal_scallop(
            canvas,
            cx=body_x + scallop_dx,
            edge_y=edge_y,
            r=scallop_r,
            body_x=body_x,
            body_w=body_w,
            cy=cy,
        )

        _draw_internal_scallop(
            canvas,
            cx=body_x + scallop_dx * 3.0,
            edge_y=edge_y,
            r=scallop_r * 0.5,
            body_x=body_x,
            body_w=body_w,
            cy=cy,
        )

    canvas.setFillColorRGB(0.75, 0.75, 0.75)

    if spec is not None and getattr(spec, "pin_pitch_mm", None) is not None:
        pitch_mm = float(getattr(spec, "pin_pitch_mm"))
    else:
        pitch_mm = 5.75 if pin_count <= 3 else 3.81

    pitch = (pitch_mm / body_mm) * draw_h
    if pitch <= 0.0:
        pitch = draw_h * 0.18

    lead_th = draw_h * 0.07

    lead_step_fraction = 0.15
    lead_step_width_scale = 2.00
    lead_step_th_max_fraction_of_pitch = 0.75

    lead_step_len = lead_w * lead_step_fraction
    lead_step_th = lead_th * lead_step_width_scale
    lead_step_th_max = pitch * lead_step_th_max_fraction_of_pitch
    if lead_step_th > lead_step_th_max:
        lead_step_th = lead_step_th_max

    offsets = compute_offsets(pin_count, pitch)
    first_pin_x = body_x + body_w

    for off in offsets:
        regular_y = cy + off - lead_th * 0.5
        step_y = cy + off - lead_step_th * 0.5

        canvas.rect(
            first_pin_x,
            step_y,
            lead_step_len,
            lead_step_th,
            fill=1,
            stroke=0,
        )

        remaining_len = lead_w - lead_step_len
        if remaining_len < 0.0:
            remaining_len = 0.0

        canvas.rect(
            first_pin_x + lead_step_len,
            regular_y,
            remaining_len,
            lead_th,
            fill=1,
            stroke=0,
        )

    if pin_count <= 3:
        fs = rect.height * 0.20
    else:
        fs = rect.height * 0.14

    min_font_fraction = 0.10
    if fs < rect.height * min_font_fraction:
        fs = rect.height * min_font_fraction

    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    label_pad = fs * 0.35
    mid = (pin_count - 1) / 2.0

    label_y_adjust: list[float] = []
    for i in range(pin_count):
        rel = i - mid
        if rel < 0.0:
            adj = -label_pad
        elif rel > 0.0:
            adj = +label_pad
        else:
            adj = 0.0
        label_y_adjust.append(adj)

    label_gap_fraction = 0.15
    label_x = first_pin_x + lead_w + (draw_h * label_gap_fraction)

    for i, off in enumerate(offsets):
        if i >= len(final_labels):
            break

        label = str(final_labels[i]).upper()
        py = cy + off + label_y_adjust[i]

        canvas.drawString(
            label_x,
            py - fs * 0.40,
            label,
        )

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
