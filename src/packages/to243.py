# file: src/packages/to243.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical


def draw_to243_package(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    *,
    default_pin_labels=None,
    spec=None,
) -> None:
    """
    @brief			Draw a TO-243 (SOT-89) package (3, 4 or 6 pin variants).

    Variants:
    - 3-pin: 1 top tab + 2 bottom pins (middle bottom pin absent).
    - 4-pin: 1 top tab + 3 bottom pins. Top tab is wider than bottom pins.
             Top tab and middle bottom pin are electrically common.
    - 6-pin: top row has 3 pins (left, tab, right) where left and right are
             same size as bottom pins. Bottom row has 3 pins.

    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param info			Package geometry dictionary (mm units)
    @param default_pin_labels	Optional default labels
    @param spec			Optional device spec (pin_config override)
    @return			None
    """
    final_labels = ["1", "2", "3", "TAB"]

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = [p.strip() for p in spec.pin_config.replace(",", " ").split()]
    elif default_pin_labels:
        final_labels = list(default_pin_labels)

    pin_count = int(info.get("pin_count", 4))
    if pin_count not in [3, 4, 6]:
        pin_count = 4

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_width_mm = float(info.get("body_w", 4.5))
    body_height_mm = float(info.get("body_h", 2.76))

    bottom_pad_width_mm = float(info.get("padb_w", 0.4))
    bottom_pad_height_mm = float(info.get("padb_h", 0.8))
    bottom_pitch_mm = float(info.get("padb_pitch", 1.5))

    top_tab_width_mm = float(info.get("tab_w", 1.6))
    top_tab_height_mm = float(info.get("tab_h", 0.8))

    top_side_pad_width_mm = float(info.get("padt_w", bottom_pad_width_mm))
    top_side_pad_height_mm = float(info.get("padt_h", bottom_pad_height_mm))
    top_pitch_mm = float(info.get("padt_pitch", bottom_pitch_mm))

    if body_width_mm <= 0.0 or body_height_mm <= 0.0:
        return
    if bottom_pad_width_mm <= 0.0 or bottom_pad_height_mm <= 0.0:
        return
    if bottom_pitch_mm <= 0.0:
        return
    if top_tab_width_mm <= 0.0 or top_tab_height_mm <= 0.0:
        return
    if pin_count == 6 and top_pitch_mm <= 0.0:
        return

    body_w, body_h = scale_physical(rect, body_width_mm, body_height_mm, 2.0)

    scale_x = body_w / body_width_mm
    scale_y = body_h / body_height_mm

    bottom_pad_w = bottom_pad_width_mm * scale_x
    bottom_pad_h = bottom_pad_height_mm * scale_y
    bottom_pitch = bottom_pitch_mm * scale_x

    top_tab_w = top_tab_width_mm * scale_x
    top_tab_h = top_tab_height_mm * scale_y

    top_side_pad_w = top_side_pad_width_mm * scale_x
    top_side_pad_h = top_side_pad_height_mm * scale_y
    top_pitch = top_pitch_mm * scale_x

    body_x = cx - body_w * 0.5
    body_y = cy - body_h * 0.5

    bottom_row_y = body_y - bottom_pad_h
    top_row_y = body_y + body_h

    pad_centres_x = []
    pad_centres_y = []
    pad_sizes = []

    if pin_count == 3:
        bottom_centres_x = [
            cx - bottom_pitch,
            cx + bottom_pitch,
        ]
    elif pin_count in [4, 6]:
        bottom_centres_x = [
            cx - bottom_pitch,
            cx,
            cx + bottom_pitch,
        ]
    else:
        bottom_centres_x = [cx - bottom_pitch, cx + bottom_pitch]

    for x in bottom_centres_x:
        pad_centres_x.append(x)
        pad_centres_y.append(bottom_row_y + (bottom_pad_h * 0.5))
        pad_sizes.append((bottom_pad_w, bottom_pad_h))

    if pin_count in [3, 4]:
        pad_centres_x.append(cx)
        pad_centres_y.append(top_row_y + (top_tab_h * 0.5))
        pad_sizes.append((top_tab_w, top_tab_h))
    else:
        top_centres_x = [
            cx - top_pitch,
            cx,
            cx + top_pitch,
        ]

        pad_centres_x.append(top_centres_x[0])
        pad_centres_y.append(top_row_y + (top_side_pad_h * 0.5))
        pad_sizes.append((top_side_pad_w, top_side_pad_h))

        pad_centres_x.append(top_centres_x[1])
        pad_centres_y.append(top_row_y + (top_tab_h * 0.5))
        pad_sizes.append((top_tab_w, top_tab_h))

        pad_centres_x.append(top_centres_x[2])
        pad_centres_y.append(top_row_y + (top_side_pad_h * 0.5))
        pad_sizes.append((top_side_pad_w, top_side_pad_h))

    canvas.setFillColorRGB(0.75, 0.75, 0.75)
    for i in range(0, len(pad_centres_x)):
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
    for i in range(0, len(pad_centres_x)):
        if i < len(final_labels):
            labels.append(str(final_labels[i]).upper())
        else:
            labels.append(str(i + 1))

    label_gap = fs * 0.75
    outward_nudge = fs * 0.55
    label_baseline_offset = fs * 0.35

    for i in range(0, len(pad_centres_x)):
        is_top = pad_centres_y[i] > cy
        pad_h = pad_sizes[i][1]
        pad_w = pad_sizes[i][0]

        delta_x = 0.0
        if pad_centres_x[i] < cx:
            delta_x = -min(outward_nudge, pad_w * 0.9)
        elif pad_centres_x[i] > cx:
            delta_x = min(outward_nudge, pad_w * 0.9)

        if is_top:
            label_y = pad_centres_y[i] + (pad_h * 0.5) + label_gap
        else:
            label_y = pad_centres_y[i] - (pad_h * 0.5) - label_gap

        label_y = label_y - label_baseline_offset

        canvas.drawCentredString(pad_centres_x[i] + delta_x, label_y, labels[i])

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
