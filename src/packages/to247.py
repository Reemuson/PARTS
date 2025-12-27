# file: src/packages/to247.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
    compute_offsets,
)


def draw_to247_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    spec: object | None = None,
) -> None:
    if pin_count not in (3, 4):
        pin_count = 3

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    elif spec is not None and getattr(spec, "pin_labels", None):
        final_labels = getattr(spec, "pin_labels")
    else:
        final_labels = default_numeric_labels(pin_count)

    body_w_mm = float(getattr(spec, "body_w", 20.1))
    body_h_mm = float(getattr(spec, "body_h", 15.9))
    lead_len_mm = float(getattr(spec, "lead_len", 20.0))

    hole_d_mm = float(getattr(spec, "hole_d_mm", 3.6))
    scallop_w_mm = float(getattr(spec, "scallop_w_mm", 4.0))
    scallop_h_mm = float(getattr(spec, "scallop_h_mm", 2.0))
    scallop_x_mm = float(getattr(spec, "scallop_x_mm", 6.2))

    pitch_3lead_mm = float(getattr(spec, "lead_pitch_3_mm", 5.44))
    pitch_group_mm = float(getattr(spec, "lead_pitch_group_mm", 2.54))
    group_gap_mm = float(getattr(spec, "group_gap_mm", 5.08))

    phys_w = body_w_mm + lead_len_mm
    phys_h = body_h_mm

    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    label_margin_fraction = 0.15
    cx = rect.left + (rect.width * (1.0 - label_margin_fraction)) * 0.5
    cy = rect.bottom + rect.height * 0.50

    x0 = cx - draw_w * 0.5
    y0 = cy - draw_h * 0.5

    body_w = draw_w * (body_w_mm / phys_w)
    lead_len = draw_w * (lead_len_mm / phys_w)

    body_x = x0
    body_y = y0
    body_h = draw_h
    lead_x = body_x + body_w

    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.rect(body_x, body_y, body_w, body_h, fill=1, stroke=0)

    hole_r = (hole_d_mm / body_h_mm) * draw_h * 0.5
    scallop_w = (scallop_w_mm / body_w_mm) * body_w
    scallop_h = (scallop_h_mm / body_h_mm) * body_h
    scallop_dx = (scallop_x_mm / body_w_mm) * body_w

    top_edge_y = body_y + body_h - scallop_h
    bot_edge_y = body_y

    canvas.setFillColorRGB(1.0, 1.0, 1.0)
    canvas.circle(
        body_x + scallop_dx,
        cy,
        hole_r,
        fill=1,
        stroke=0,
    )

    canvas.setFillColorRGB(0.25, 0.25, 0.25)
    for edge_y in (top_edge_y, bot_edge_y):
        canvas.rect(
            body_x + scallop_dx - scallop_w * 0.5,
            edge_y,
            scallop_w,
            scallop_h,
            fill=1,
            stroke=0,
        )

    canvas.setFillColorRGB(0.75, 0.75, 0.75)

    lead_th = body_h * 0.07

    lead_step_fraction = 0.15
    lead_step_width_scale = 2.00

    lead_step_len = lead_len * lead_step_fraction
    lead_step_th = lead_th * lead_step_width_scale
    lead_step_th_max = body_h * 0.30
    if lead_step_th > lead_step_th_max:
        lead_step_th = lead_step_th_max

    if pin_count == 3:
        pitch = (pitch_3lead_mm / body_h_mm) * body_h
        if pitch <= 0.0:
            pitch = body_h * 0.18
        offsets = compute_offsets(3, pitch)
    else:
        pitch_group = (pitch_group_mm / body_h_mm) * body_h
        if pitch_group <= 0.0:
            pitch_group = body_h * 0.10

        group_gap = (group_gap_mm / body_h_mm) * body_h
        if group_gap < pitch_group * 0.5:
            group_gap = pitch_group * 0.5

        group_offsets = compute_offsets(3, pitch_group)

        pin2_off = min(group_offsets)
        pin3_off = group_offsets[1]
        pin4_off = max(group_offsets)

        offset_shift = -pin2_off
        pin2_off = pin2_off + offset_shift
        pin3_off = pin3_off + offset_shift
        pin4_off = pin4_off + offset_shift

        pin1_off = pin2_off - group_gap

        offsets = [pin1_off, pin2_off, pin3_off, pin4_off]

    for off in offsets:
        regular_y = cy + off - lead_th * 0.5
        step_y = cy + off - lead_step_th * 0.5

        canvas.rect(
            lead_x,
            step_y,
            lead_step_len,
            lead_step_th,
            fill=1,
            stroke=0,
        )

        remaining_len = lead_len - lead_step_len
        if remaining_len < 0.0:
            remaining_len = 0.0

        canvas.rect(
            lead_x + lead_step_len,
            regular_y,
            remaining_len,
            lead_th,
            fill=1,
            stroke=0,
        )

    if pin_count <= 4:
        fs = rect.height * 0.20
    else:
        fs = rect.height * (0.20 - 0.03 * (pin_count - 4))

    min_font_fraction = 0.10
    if fs < rect.height * min_font_fraction:
        fs = rect.height * min_font_fraction

    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    label_pad = fs * 0.35

    label_gap_fraction = 0.15
    label_x = lead_x + lead_len + (draw_h * label_gap_fraction)

    if pin_count == 4:
        label_y_adjust = [-label_pad, -label_pad, 0.0, +label_pad]
    else:
        label_mid = (len(offsets) - 1) / 2.0
        label_y_adjust: list[float] = []
        for j in range(len(offsets)):
            rel = j - label_mid
            if rel < 0.0:
                adj = -label_pad
            elif rel > 0.0:
                adj = +label_pad
            else:
                adj = 0.0
            label_y_adjust.append(adj)

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
