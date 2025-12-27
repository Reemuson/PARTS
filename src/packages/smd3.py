# file: src/packages/smd3.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical


def draw_smd3_package(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    *,
    default_pin_labels=None,
    spec=None,
) -> None:
    """
    @brief			Draw a 3-pad SMD package with 2 pads on bottom, 1 on top.

    Default geometry matches SOT-23 if fields are missing in info.
    All geometry inputs are in mm.

    Pad pitch definition:
    - pad2_pitch is centre-to-centre spacing between the two bottom pads.

    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param info			Package geometry dictionary (mm units)
    @param default_pin_labels	Optional default labels
    @param spec			Optional device spec (pin_config override)
    @return			None
    """
    final_labels = ["1", "2", "3"]

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = [p.strip() for p in spec.pin_config.replace(",", " ").split()]
    elif default_pin_labels:
        final_labels = list(default_pin_labels)

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_width_mm = float(info.get("body_w", 2.9))
    body_height_mm = float(info.get("body_h", 1.3))

    bottom_pad_width_mm = float(info.get("pad2_w", 0.41))
    bottom_pad_height_mm = float(info.get("pad2_h", 0.6))
    bottom_pitch_mm = float(info.get("pad2_pitch", 1.9))

    top_pad_width_mm = float(info.get("pad1_w", 0.41))
    top_pad_height_mm = float(info.get("pad1_h", 0.6))

    if body_width_mm <= 0.0 or body_height_mm <= 0.0:
        return
    if bottom_pad_width_mm <= 0.0 or bottom_pad_height_mm <= 0.0:
        return
    if top_pad_width_mm <= 0.0 or top_pad_height_mm <= 0.0:
        return
    if bottom_pitch_mm <= 0.0:
        return

    body_w, body_h = scale_physical(rect, body_width_mm, body_height_mm, 3.0)

    scale_x = body_w / body_width_mm
    scale_y = body_h / body_height_mm

    bottom_pad_w = bottom_pad_width_mm * scale_x
    bottom_pad_h = bottom_pad_height_mm * scale_y
    bottom_pitch = bottom_pitch_mm * scale_x

    top_pad_w = top_pad_width_mm * scale_x
    top_pad_h = top_pad_height_mm * scale_y

    body_x = cx - body_w * 0.5
    body_y = cy - body_h * 0.5

    bottom_row_y = body_y - bottom_pad_h
    top_row_y = body_y + body_h

    pad_1_cx = cx - (bottom_pitch * 0.5)
    pad_2_cx = cx + (bottom_pitch * 0.5)
    pad_3_cx = cx

    pad_1_x = pad_1_cx - (bottom_pad_w * 0.5)
    pad_2_x = pad_2_cx - (bottom_pad_w * 0.5)
    pad_3_x = pad_3_cx - (top_pad_w * 0.5)

    canvas.setFillColorRGB(0.75, 0.75, 0.75)
    canvas.rect(
        pad_1_x,
        bottom_row_y,
        bottom_pad_w,
        bottom_pad_h,
        fill=1,
        stroke=0,
    )
    canvas.rect(
        pad_2_x,
        bottom_row_y,
        bottom_pad_w,
        bottom_pad_h,
        fill=1,
        stroke=0,
    )
    canvas.rect(
        pad_3_x,
        top_row_y,
        top_pad_w,
        top_pad_h,
        fill=1,
        stroke=0,
    )

    stroke_width = 1.0
    body_inner_w = max(0.0, body_w - stroke_width)
    body_inner_h = max(0.0, body_h - stroke_width)

    body_inner_x = cx - (body_inner_w * 0.5)
    body_inner_y = cy - (body_inner_h * 0.5)

    canvas.setLineWidth(stroke_width)
    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.setStrokeColorRGB(0.2, 0.2, 0.2)
    canvas.rect(
        body_inner_x,
        body_inner_y,
        body_inner_w,
        body_inner_h,
        fill=1,
        stroke=1,
    )

    pin_one_dot_r = min(body_inner_w, body_inner_h) * 0.07
    pin_one_dot_x = body_inner_x + (pin_one_dot_r * 1.8)
    pin_one_dot_y = body_inner_y + body_inner_h - (pin_one_dot_r * 1.8)
    canvas.setFillColorRGB(0.60, 0.60, 0.60)
    canvas.circle(
        pin_one_dot_x,
        pin_one_dot_y,
        pin_one_dot_r,
        stroke=0,
        fill=1,
    )

    fs = rect.height * 0.25
    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    label_1 = str(final_labels[0]).upper() if len(final_labels) > 0 else "1"
    label_2 = str(final_labels[1]).upper() if len(final_labels) > 1 else "2"
    label_3 = str(final_labels[2]).upper() if len(final_labels) > 2 else "3"

    bottom_label_y = bottom_row_y - (fs * 0.90)
    top_label_y = top_row_y + top_pad_h + (fs * 0.10)

    canvas.drawCentredString(pad_1_cx, bottom_label_y, label_1)
    canvas.drawCentredString(pad_2_cx, bottom_label_y, label_2)
    canvas.drawCentredString(pad_3_cx, top_label_y, label_3)

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
