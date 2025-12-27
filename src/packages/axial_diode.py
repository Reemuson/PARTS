# file: src/packages/axial_diode.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical


AXIAL_LEAD_FRACTION = 0.18
SMD_CAP_OVERLAP_FRACTION = 0.02


def _draw_axial_labels_tht(
    canvas: Canvas,
    rect: simple_rect,
    *,
    body_x: float,
    body_w: float,
    cy: float,
) -> None:
    """
    @brief		Draw A/K labels for THT axial packages.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param body_x	Body left x
    @param body_w	Body width
    @param cy		Centre y
    @return		None
    """
    fs = rect.height * 0.25
    canvas.setFillColor(black)
    canvas.setFont("Helvetica", fs)

    a_x = body_x - (rect.width * AXIAL_LEAD_FRACTION * 0.5)
    k_x = body_x + body_w + (rect.width * AXIAL_LEAD_FRACTION * 0.5)
    label_y = cy + fs * 0.35

    a_text = "A"
    k_text = "K"

    a_w = canvas.stringWidth(a_text, "Helvetica", fs)
    k_w = canvas.stringWidth(k_text, "Helvetica", fs)

    canvas.drawString(a_x - a_w * 0.5, label_y, a_text)
    canvas.drawString(k_x - k_w * 0.5, label_y, k_text)


def _draw_axial_labels_smd(
    canvas: Canvas,
    rect: simple_rect,
    *,
    left_pad_outer_x: float,
    right_pad_outer_x: float,
    pad_y: float,
    pad_h: float,
    pad_w: float,
) -> None:
    """
    @brief			Draw A/K labels for SMD axial (MELF style) packages.

    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param left_pad_outer_x	Left pad outer edge x
    @param right_pad_outer_x	Right pad outer edge x
    @param pad_y		Pad bottom y
    @param pad_h		Pad height
    @param pad_w		Pad width
    @return			None
    """
    fs = rect.height * 0.25
    canvas.setFillColor(black)
    canvas.setFont("Helvetica", fs)

    pad_centre_y = pad_y + (pad_h * 0.5)
    text_y = pad_centre_y - (fs * 0.35)

    a_text = "A"
    k_text = "K"

    a_w = canvas.stringWidth(a_text, "Helvetica", fs)
    k_w = canvas.stringWidth(k_text, "Helvetica", fs)

    gap = pad_w * 0.60

    canvas.drawString(left_pad_outer_x - gap - a_w, text_y, a_text)
    canvas.drawString(right_pad_outer_x + gap, text_y, k_text)


def draw_axial_package(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    material: str,
    show_labels: bool = True,
) -> None:
    """
    @brief		Draw a cylindrical axial package in THT or MELF-style SMD form.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param info		Param dictionary (dimensions, mount, pad sizing)
    @param material	Material/colour selector (glass, epoxy, metallic, blue)
    @param show_labels	Draw A/K labels
    @return		None
    """
    mount_style = str(info.get("mount", "tht")).strip().lower()

    body_length_mm = float(info.get("body_length", info.get("len", 0.0)))
    body_diameter_mm = float(info.get("body_diameter", info.get("dia", 0.0)))

    if body_length_mm <= 0.0 or body_diameter_mm <= 0.0:
        return

    pad_end_length_mm = info.get("pad_end_length", info.get("pad_width", None))
    pad_height_mm = info.get("pad_height", None)

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5

    body_w, body_h = scale_physical(rect, body_length_mm, body_diameter_mm, 2.0)

    body_x = cx - body_w * 0.5
    body_y = cy - body_h * 0.5

    material_norm = (material or "").strip().lower()

    if material_norm == "glass":
        mid_col = (0.78, 0.32, 0.06)
        top_col = (0.90, 0.40, 0.10)
        bot_col = (0.40, 0.16, 0.03)
        band_col = (0.0, 0.0, 0.0)
    elif material_norm == "metallic":
        top_col = (0.90, 0.90, 0.92)
        mid_col = (0.70, 0.70, 0.72)
        bot_col = (0.35, 0.35, 0.38)
        band_col = (0.0, 0.0, 0.0)
    elif material_norm == "blue":
        top_col = (0.20, 0.65, 1.00)
        mid_col = (0.00, 0.50, 0.78)
        bot_col = (0.00, 0.25, 0.45)
        band_col = (0.0, 0.0, 0.0)
    else:
        mid_col = (0.30, 0.30, 0.30)
        top_col = (0.45, 0.45, 0.45)
        bot_col = (0.06, 0.06, 0.06)
        band_col = (0.75, 0.75, 0.75)

    pad_w = 0.0
    pad_h = 0.0
    cap_overlap = 0.0

    left_pad_outer_x = 0.0
    right_pad_outer_x = 0.0
    pad_y = 0.0

    if mount_style == "smd":
        if pad_end_length_mm is None:
            pad_end_length_mm = body_diameter_mm * 0.55
        if pad_height_mm is None:
            pad_height_mm = body_diameter_mm * 1.30

        if float(pad_end_length_mm) < 0.0:
            pad_end_length_mm = 0.0

        scale_x = body_w / body_length_mm
        scale_y = body_h / body_diameter_mm

        pad_w = float(pad_end_length_mm) * scale_x
        pad_h = float(pad_height_mm) * scale_y

        if pad_w > (body_w * 0.5):
            pad_w = body_w * 0.5

        if pad_h < body_h:
            pad_h = body_h

        cap_overlap = max(body_w * SMD_CAP_OVERLAP_FRACTION, 0.4)

        pad_y = cy - pad_h * 0.5

        left_pad_x = body_x - cap_overlap
        left_pad_w = pad_w + cap_overlap

        right_pad_x = body_x + body_w - pad_w
        right_pad_w = pad_w + cap_overlap

        left_pad_outer_x = left_pad_x
        right_pad_outer_x = right_pad_x + right_pad_w
    else:
        lead_len = rect.width * AXIAL_LEAD_FRACTION
        left_lead_start = cx - body_w * 0.5 - lead_len
        left_lead_end = cx - body_w * 0.5
        right_lead_start = cx + body_w * 0.5
        right_lead_end = cx + body_w * 0.5 + lead_len

        canvas.setStrokeColor(black)
        canvas.setLineWidth(1.0)
        canvas.line(left_lead_start, cy, left_lead_end, cy)
        canvas.line(right_lead_start, cy, right_lead_end, cy)

    canvas.saveState()
    path_top = canvas.beginPath()
    path_top.rect(body_x, body_y + body_h * 0.5, body_w, body_h * 0.5)
    canvas.clipPath(path_top, stroke=0)
    canvas.linearGradient(
        body_x + body_w * 0.5,
        body_y + body_h,
        body_x + body_w * 0.5,
        body_y + body_h * 0.5,
        (top_col, mid_col),
    )
    canvas.restoreState()

    canvas.saveState()
    path_bot = canvas.beginPath()
    path_bot.rect(body_x, body_y, body_w, body_h * 0.5)
    canvas.clipPath(path_bot, stroke=0)
    canvas.linearGradient(
        body_x + body_w * 0.5,
        body_y + body_h * 0.5,
        body_x + body_w * 0.5,
        body_y,
        (mid_col, bot_col),
    )
    canvas.restoreState()

    band_w = body_w * 0.16
    band_x = body_x + body_w - band_w

    if mount_style == "smd" and pad_w > 0.0:
        band_x = body_x + body_w - pad_w - band_w
        if band_x < body_x:
            band_x = body_x

    canvas.setFillColorRGB(*band_col)
    canvas.rect(band_x, body_y, band_w, body_h, fill=1, stroke=0)

    if mount_style == "smd" and pad_w > 0.0:
        left_pad_x = body_x - cap_overlap
        left_pad_w = pad_w + cap_overlap

        right_pad_x = body_x + body_w - pad_w
        right_pad_w = pad_w + cap_overlap

        canvas.setFillColorRGB(0.80, 0.80, 0.82)
        canvas.rect(left_pad_x, pad_y, left_pad_w, pad_h, fill=1, stroke=0)
        canvas.rect(right_pad_x, pad_y, right_pad_w, pad_h, fill=1, stroke=0)

    if show_labels:
        if mount_style == "smd" and pad_w > 0.0:
            _draw_axial_labels_smd(
                canvas,
                rect,
                left_pad_outer_x=left_pad_outer_x,
                right_pad_outer_x=right_pad_outer_x,
                pad_y=pad_y,
                pad_h=pad_h,
                pad_w=pad_w,
            )
        else:
            _draw_axial_labels_tht(
                canvas,
                rect,
                body_x=body_x,
                body_w=body_w,
                cy=cy,
            )

    canvas.setFillColor(black)
    canvas.setStrokeColor(black)
