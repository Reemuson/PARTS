# file: src/packages/to220.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
    compute_offsets,
)


def draw_to220_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    spec: object | None = None,
) -> None:
    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    elif spec is not None and getattr(spec, "pin_labels", None):
        final_labels = getattr(spec, "pin_labels")
    else:
        final_labels = default_numeric_labels(pin_count)

    tab_mm = float(getattr(spec, "tab_mm", 6.5))
    body_mm = float(getattr(spec, "body_mm", 9.5))
    lead_mm = float(getattr(spec, "lead_mm", 11.0))
    width_mm = float(getattr(spec, "width_mm", 10.0))

    tab_finish = str(getattr(spec, "tab_finish", "metallic")).lower()

    total_mm = tab_mm + body_mm + lead_mm
    phys_w = total_mm
    phys_h = width_mm

    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    label_margin_fraction = 0.15
    cx = rect.left + (rect.width * (1.0 - label_margin_fraction)) * 0.5
    cy = rect.bottom + rect.height * 0.50

    x0 = cx - draw_w * 0.5
    y0 = cy - draw_h * 0.5

    tab_w = draw_w * (tab_mm / total_mm)
    body_w = draw_w * (body_mm / total_mm)
    lead_w = draw_w * (lead_mm / total_mm)

    tab_x = x0
    if tab_finish == "insulated":
        canvas.setFillColorRGB(0.12, 0.12, 0.12)
    else:
        canvas.setFillColorRGB(0.82, 0.82, 0.82)
    canvas.rect(tab_x, y0, tab_w, draw_h, fill=1, stroke=0)

    hole_r = draw_h * 0.22
    canvas.setFillColorRGB(1.0, 1.0, 1.0)
    canvas.circle(tab_x + tab_w * 0.5, cy, hole_r, fill=1, stroke=0)

    body_x = tab_x + tab_w
    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.rect(body_x, y0, body_w, draw_h, fill=1, stroke=0)

    canvas.setFillColorRGB(0.75, 0.75, 0.75)

    pitch = draw_h * 0.30
    lead_th = draw_h * 0.08

    lead_step_fraction = 0.20
    lead_step_width_scale = 1.50
    lead_step_th_max_fraction_of_pitch = 0.75

    lead_step_len = lead_w * lead_step_fraction
    lead_step_th = lead_th * lead_step_width_scale
    lead_step_th_max = pitch * lead_step_th_max_fraction_of_pitch
    if lead_step_th > lead_step_th_max:
        lead_step_th = lead_step_th_max

    draw_pin_count = pin_count
    if pin_count == 2:
        draw_pin_count = 3

    offsets = compute_offsets(draw_pin_count, pitch)
    first_pin_x = body_x + body_w

    for i, off in enumerate(offsets):
        regular_y = cy + off - lead_th * 0.5
        step_y = cy + off - lead_step_th * 0.5

        is_stub_pin = (pin_count == 2) and (i == 1)
        draw_tail = not is_stub_pin

        canvas.rect(
            first_pin_x,
            step_y,
            lead_step_len,
            lead_step_th,
            fill=1,
            stroke=0,
        )

        if draw_tail:
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
    label_mid = (draw_pin_count - 1) / 2.0

    label_y_adjust: list[float] = []
    for i in range(draw_pin_count):
        rel = i - label_mid
        if rel < 0.0:
            adj = -label_pad
        elif rel > 0.0:
            adj = +label_pad
        else:
            adj = 0.0
        label_y_adjust.append(adj)

    label_gap_fraction = 0.15
    label_x = first_pin_x + lead_w + (draw_h * label_gap_fraction)

    if pin_count == 2:
        label_indices = [0, 2]
    else:
        label_indices = list(range(draw_pin_count))

    for i, idx in enumerate(label_indices):
        if i >= len(final_labels):
            break

        label = str(final_labels[i]).upper()
        off = offsets[idx]
        adj = label_y_adjust[idx]

        py = cy + off + adj

        canvas.drawString(
            label_x,
            py - fs * 0.40,
            label,
        )

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
