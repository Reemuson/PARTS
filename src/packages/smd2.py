# file: src/packages/smd2.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical


def draw_smd2_package(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    *,
    default_pin_labels=None,
    spec=None,
) -> None:
    """
    @brief			Draw a 2-pad SMD diode package (eg DO-214, SOD-123).

    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param info			Package geometry dictionary
    @param default_pin_labels	Optional default labels (A/K)
    @param spec			Optional device spec (pin_config override)
    @return			None
    """
    final_labels = ["A", "K"]

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = [p.strip() for p in spec.pin_config.replace(",", " ").split()]
    elif default_pin_labels:
        final_labels = list(default_pin_labels)

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_width_mm = float(info.get("body_w", 0.0))
    body_height_mm = float(info.get("body_h", 0.0))
    pad_width_mm = float(info.get("pad_w", 0.0))
    pad_height_mm = float(info.get("pad_h", 0.0))

    if body_width_mm <= 0.0 or body_height_mm <= 0.0:
        return
    if pad_width_mm <= 0.0 or pad_height_mm <= 0.0:
        return

    body_w, body_h = scale_physical(rect, body_width_mm, body_height_mm, 2.0)

    scale_x = body_w / body_width_mm
    scale_y = body_h / body_height_mm

    pad_w = pad_width_mm * scale_x
    pad_h = pad_height_mm * scale_y

    body_x = cx - body_w * 0.5
    body_y = cy - body_h * 0.5

    left_pad_x = body_x - pad_w
    right_pad_x = body_x + body_w
    pad_y = cy - pad_h * 0.5

    canvas.setFillColorRGB(0.75, 0.75, 0.75)
    canvas.rect(left_pad_x, pad_y, pad_w, pad_h, fill=1, stroke=0)
    canvas.rect(right_pad_x, pad_y, pad_w, pad_h, fill=1, stroke=0)

    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.setStrokeColorRGB(0.2, 0.2, 0.2)
    canvas.rect(body_x, body_y, body_w, body_h, fill=1, stroke=1)

    stripe_w = body_w * 0.15
    canvas.setFillColorRGB(0.60, 0.60, 0.60)
    canvas.rect(body_x + body_w - stripe_w, body_y, stripe_w, body_h, fill=1, stroke=0)

    fs = rect.height * 0.25
    canvas.setFont("Helvetica", fs)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    a_label = str(final_labels[0]).upper() if len(final_labels) > 0 else "A"
    k_label = str(final_labels[1]).upper() if len(final_labels) > 1 else "K"

    left_pad_outer_x = left_pad_x
    right_pad_outer_x = right_pad_x + pad_w

    pad_centre_y = pad_y + (pad_h * 0.5)
    text_y = pad_centre_y - (fs * 0.35)

    a_text_w = canvas.stringWidth(a_label, "Helvetica", fs)
    k_text_w = canvas.stringWidth(k_label, "Helvetica", fs)

    gap = pad_w * 0.60

    canvas.drawString(left_pad_outer_x - gap - a_text_w, text_y, a_label)
    canvas.drawString(right_pad_outer_x + gap, text_y, k_label)

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
