# file: src/packages/to225.py

from math import cos, sin, radians

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
)


def draw_to225_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int = 3,
    spec: object | None = None,
) -> None:
    """@brief Draw a TO-225 / TO-126 style package."""

    # --------------------------------------------------------
    # Resolve pin labels
    # --------------------------------------------------------
    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(spec.pin_config)
    else:
        final_labels = default_numeric_labels(pin_count)

    # --------------------------------------------------------
    # Dimensions from DB / spec
    # --------------------------------------------------------
    body_w_mm = float(getattr(spec, "body_w", 8.0))
    body_h_mm = float(getattr(spec, "body_h", 11.0))
    lead_len_mm = float(getattr(spec, "lead_len", 16.0))
    lead_pitch_mm = float(getattr(spec, "lead_pitch", 2.54))
    hole_d_mm = float(getattr(spec, "hole_d", 3.20))

    phys_w = body_w_mm + lead_len_mm
    phys_h = body_h_mm

    # Scale into label rect
    draw_w, draw_h = scale_physical(rect, phys_w, phys_h, 2.0)

    # Centre slightly left so leads fit on the right
    cx = rect.left + rect.width * 0.40
    cy = rect.bottom + rect.height * 0.50

    x0 = cx - draw_w * 0.5
    y0 = cy - draw_h * 0.5

    # --------------------------------------------------------
    # Main body
    # --------------------------------------------------------
    body_w_vert = draw_w * (body_w_mm / phys_w)
    body_h_vert = draw_h

    body_cx = x0 + body_w_vert * 0.5
    body_cy = y0 + body_h_vert * 0.5

    body_w = body_h_vert
    body_h = body_w_vert

    x0 = body_cx - body_w * 0.5
    y0 = body_cy - body_h * 0.5

    canvas.setFillColorRGB(0.12, 0.12, 0.12)  # epoxy black
    canvas.rect(x0, y0, body_w, body_h, fill=1, stroke=0)

    # --------------------------------------------------------
    # Mounting hole + reinforcement bosses
    # --------------------------------------------------------
    hole_r = draw_w * (hole_d_mm / phys_w) * 0.5
    hole_x = x0 + body_h * 0.5
    hole_y = cy

    canvas.setFillColorRGB(0.25, 0.25, 0.25)
    back_r = hole_r * 1.50
    for angle in (0, 120, 240):
        ax = hole_x + back_r * 0.70 * cos(radians(angle))
        ay = hole_y + back_r * 0.70 * sin(radians(angle))
        canvas.circle(ax, ay, hole_r * 0.65, fill=1, stroke=0)

    canvas.setFillColorRGB(1, 1, 1)
    canvas.circle(hole_x, hole_y, hole_r, fill=1, stroke=0)

    # --------------------------------------------------------
    # Leads
    # --------------------------------------------------------
    canvas.setFillColorRGB(0.75, 0.75, 0.75)  # silver

    lead_len = draw_w * (lead_len_mm / phys_w)
    lead_th = body_h * 0.12

    # Pitch referenced to physical body height so spacing stays
    # consistent after rotation.
    draw_pitch = (lead_pitch_mm / body_h_mm) * body_h

    # 3-pin layout: [-pitch, 0, +pitch]
    offsets = [
        cy - draw_pitch,
        cy,
        cy + draw_pitch,
    ]

    lead_start_x = x0 + body_w

    for y in offsets:
        canvas.rect(
            lead_start_x,
            y - lead_th * 0.5,
            lead_len,
            lead_th,
            fill=1,
            stroke=0,
        )

    # --------------------------------------------------------
    # Pin labels
    # --------------------------------------------------------
    fs = rect.height * 0.18
    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0, 0, 0)

    label_pad = fs * 0.40
    label_offset = [-label_pad, 0, +label_pad]

    for i, y in enumerate(offsets):
        if i >= len(final_labels):
            break

        canvas.drawString(
            lead_start_x + lead_len + fs * 0.4,
            y + label_offset[i] - fs * 0.4,
            final_labels[i].upper(),
        )

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
