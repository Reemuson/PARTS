# file: src/packages/smd4.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical


def draw_smd4_package(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    *,
    default_pin_labels=None,
    spec=None,
) -> None:
    """
    @brief	Draw a 4-pad SMD package with configurable row split.

    Supported layouts:
    - 1 top, 3 bottom	(row_split="1_3")
    - 2 top, 2 bottom	(row_split="2_2")

    Geometry inputs are in mm.

    Pad pitch definition:
    - bottom_pitch is centre-to-centre spacing between adjacent bottom pads
    - top_pitch is centre-to-centre spacing between adjacent top pads

    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param info			Package geometry dictionary (mm units)
    @param default_pin_labels	Optional default labels
    @param spec			Optional device spec (pin_config override)
    @return			None
    """
    final_labels = ["1", "2", "3", "4"]

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = [p.strip() for p in spec.pin_config.replace(",", " ").split()]
    elif default_pin_labels:
        final_labels = list(default_pin_labels)

    row_split = str(info.get("row_split", "1_3")).strip().lower()
    if row_split not in ["1_3", "2_2"]:
        row_split = "1_3"

    body_width_mm = float(info.get("body_w", 0.0))
    body_height_mm = float(info.get("body_h", 0.0))

    bottom_pad_width_mm = float(info.get("padb_w", 0.0))
    bottom_pad_height_mm = float(info.get("padb_h", 0.0))
    bottom_pitch_mm = float(info.get("padb_pitch", 0.0))

    top_pad_width_mm = float(info.get("padt_w", 0.0))
    top_pad_height_mm = float(info.get("padt_h", 0.0))
    top_pitch_mm = float(info.get("padt_pitch", bottom_pitch_mm))

    if body_width_mm <= 0.0 or body_height_mm <= 0.0:
        return
    if bottom_pad_width_mm <= 0.0 or bottom_pad_height_mm <= 0.0:
        return
    if top_pad_width_mm <= 0.0 or top_pad_height_mm <= 0.0:
        return
    if bottom_pitch_mm <= 0.0:
        return
    if row_split == "2_2" and top_pitch_mm <= 0.0:
        return

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_w, body_h = scale_physical(rect, body_width_mm, body_height_mm, 2.0)

    scale_x = body_w / body_width_mm
    scale_y = body_h / body_height_mm

    bottom_pad_w = bottom_pad_width_mm * scale_x
    bottom_pad_h = bottom_pad_height_mm * scale_y
    bottom_pitch = bottom_pitch_mm * scale_x

    top_pad_w = top_pad_width_mm * scale_x
    top_pad_h = top_pad_height_mm * scale_y
    top_pitch = top_pitch_mm * scale_x

    body_y = cy - body_h * 0.5

    bottom_row_y = body_y - bottom_pad_h
    top_row_y = body_y + body_h

    pad_centres_x = []
    pad_centres_y = []
    pad_sizes = []

    if row_split == "1_3":
        bottom_centres = [
            cx - bottom_pitch,
            cx,
            cx + bottom_pitch,
        ]
        top_centres = [cx]

        pad_centres_x.extend(bottom_centres)
        pad_centres_y.extend([bottom_row_y + (bottom_pad_h * 0.5)] * 3)
        pad_sizes.extend([(bottom_pad_w, bottom_pad_h)] * 3)

        pad_centres_x.extend(top_centres)
        pad_centres_y.extend([top_row_y + (top_pad_h * 0.5)] * 1)
        pad_sizes.extend([(top_pad_w, top_pad_h)] * 1)
    else:
        bottom_centres = [
            cx - (bottom_pitch * 0.5),
            cx + (bottom_pitch * 0.5),
        ]
        top_centres = [
            cx - (top_pitch * 0.5),
            cx + (top_pitch * 0.5),
        ]

        pad_centres_x.extend(bottom_centres)
        pad_centres_y.extend([bottom_row_y + (bottom_pad_h * 0.5)] * 2)
        pad_sizes.extend([(bottom_pad_w, bottom_pad_h)] * 2)

        pad_centres_x.extend(top_centres)
        pad_centres_y.extend([top_row_y + (top_pad_h * 0.5)] * 2)
        pad_sizes.extend([(top_pad_w, top_pad_h)] * 2)

    canvas.setFillColorRGB(0.75, 0.75, 0.75)
    for i in range(0, 4):
        pad_w, pad_h = pad_sizes[i]
        pad_x = pad_centres_x[i] - (pad_w * 0.5)
        pad_y = pad_centres_y[i] - (pad_h * 0.5)
        canvas.rect(pad_x, pad_y, pad_w, pad_h, fill=1, stroke=0)

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

    labels = []
    for i in range(0, 4):
        if i < len(final_labels):
            labels.append(str(final_labels[i]).upper())
        else:
            labels.append(str(i + 1))

    label_gap = fs * 0.75

    for i in range(0, 4):
        is_top = False
        if row_split == "1_3":
            is_top = i == 3
        else:
            is_top = i >= 2

        label_y = pad_centres_y[i]
        if is_top:
            label_y = pad_centres_y[i] + (pad_sizes[i][1] * 0.5) + label_gap
        else:
            label_y = pad_centres_y[i] - (pad_sizes[i][1] * 0.5) - label_gap

        canvas.drawCentredString(pad_centres_x[i], label_y, labels[i])

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
