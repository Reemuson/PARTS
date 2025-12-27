# file: src/packages/to92.py

from typing import List, Optional
from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
)


def draw_to92_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int = 3,
    spec: object | None = None,
) -> None:
    """ @brief Draw a TO-92 package rotated so the leads point to the right."""

    # --------------------------------------------------------
    # Resolve pin labels (E B C or G D S or numeric)
    # --------------------------------------------------------
    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    else:
        final_labels = default_numeric_labels(pin_count)

    # --------------------------------------------------------
    # Read dimensions from spec/db
    # --------------------------------------------------------
    body_h_mm = float(getattr(spec, "body_h", 4.8))
    body_w_mm = float(
        getattr(spec, "body_w", 4.8)
    )  # width = height; square epoxy block
    lead_len_mm = float(getattr(spec, "lead_len", 14.0))
    lead_pitch_mm = float(getattr(spec, "lead_pitch", 1.27))

    # Total physical bounding box (mm)
    # Body at left, leads extending to right
    phys_w = body_w_mm + lead_len_mm
    phys_h = body_h_mm

    # Convert to drawing units
    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    # Slight left bias for pin labels on the right
    cx = rect.left + rect.width * 0.45
    cy = rect.bottom + rect.height * 0.50

    x0 = cx - draw_w * 0.5
    y0 = cy - draw_h * 0.5

    # --------------------------------------------------------
    # Draw body (simple rectangle)
    # --------------------------------------------------------
    body_w = draw_w * (body_w_mm / phys_w)
    body_h = draw_h

    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.rect(x0, y0, body_w, body_h, fill=1, stroke=0)

    # --------------------------------------------------------
    # Leads extending right
    # --------------------------------------------------------
    canvas.setFillColorRGB(0.75, 0.75, 0.75)

    lead_len = draw_w * (lead_len_mm / phys_w)
    lead_th = body_h * 0.12

    # vertical spacing from actual TO-92 pitch
    draw_pitch = (lead_pitch_mm / body_h_mm) * body_h

    y_offsets = [
        cy - draw_pitch,
        cy,
        cy + draw_pitch,
    ]

    lead_start_x = x0 + body_w

    for y in y_offsets:
        canvas.rect(
            lead_start_x, y - lead_th * 0.5, lead_len, lead_th, fill=1, stroke=0
        )

    # --------------------------------------------------------
    # Pin labels on far right
    # --------------------------------------------------------
    fs = rect.height * 0.18
    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0, 0, 0)

    label_pad = fs * 0.50

    label_y_adjust = [
        -label_pad,
        0.0,
        +label_pad,
    ]

    for i, y in enumerate(y_offsets):
        if i >= len(final_labels):
            break

        label = final_labels[i].upper()
        adj = label_y_adjust[i]

        canvas.drawString(
            lead_start_x + lead_len + fs * 0.5,
            (y + adj) - fs * 0.4,
            label,
        )

    # Reset colours
    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
