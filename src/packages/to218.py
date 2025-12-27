# file: src/packages/to218.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.packages.tht_helpers import (
    parse_pin_config,
    default_numeric_labels,
    compute_offsets,
)


def _draw_tab_with_side_chamfers(
    canvas: Canvas,
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    chamfer: float,
    fill: int,
    stroke: int,
) -> None:
    """
    @brief		Draw the tab with chamfers on the left edge corners.
    @param canvas	ReportLab canvas
    @param x		Left of tab
    @param y		Bottom of tab
    @param w		Tab width
    @param h		Tab height
    @param chamfer	Chamfer size
    @param fill		ReportLab fill flag
    @param stroke	ReportLab stroke flag
    """
    c = chamfer
    if c < 0.0:
        c = 0.0
    if c > w * 0.45:
        c = w * 0.45
    if c > h * 0.45:
        c = h * 0.45

    path = canvas.beginPath()
    path.moveTo(x + c, y)
    path.lineTo(x + w, y)
    path.lineTo(x + w, y + h)
    path.lineTo(x + c, y + h)
    path.lineTo(x, y + h - c)
    path.lineTo(x, y + c)
    path.close()

    canvas.drawPath(path, fill=fill, stroke=stroke)


def _draw_internal_semicircle(
    canvas: Canvas,
    *,
    cx: float,
    edge_y: float,
    r: float,
    body_x: float,
    body_w: float,
    body_y: float,
    body_h: float,
) -> None:
    """
    @brief		Draw a circular scallop clipped so only the portion inside the body
                        is filled, creating an internal semicircle.
    @param canvas	ReportLab canvas
    @param cx		Scallop centre X
    @param edge_y	Body edge Y the scallop is anchored to
    @param r		Scallop radius
    @param body_x	Body left X
    @param body_w	Body width
    @param body_y	Body bottom Y
    @param body_h	Body height
    """
    canvas.saveState()

    circle_path = canvas.beginPath()
    circle_path.circle(cx, edge_y, r)
    canvas.clipPath(circle_path, stroke=0, fill=0)

    if edge_y > body_y + (body_h * 0.5):
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


def draw_to218_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    spec: object | None = None,
) -> None:
    """
    @brief		Draw a TO-218 package (3 or 5 leads) in side view.
    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pin_count	3 or 5
    @param spec		Resolved package params and optional pin metadata
    """
    if pin_count not in (3, 5):
        pin_count = 3

    if spec is not None and getattr(spec, "pin_config", None):
        final_labels = parse_pin_config(getattr(spec, "pin_config"))
    elif spec is not None and getattr(spec, "pin_labels", None):
        final_labels = getattr(spec, "pin_labels")
    else:
        final_labels = default_numeric_labels(pin_count)

    tab_mm = float(getattr(spec, "tab_mm", 8.0))
    body_mm = float(getattr(spec, "body_mm", 12.5))
    lead_mm = float(getattr(spec, "lead_mm", 11.9))
    width_mm = float(getattr(spec, "width_mm", 15.0))
    hole_d = float(getattr(spec, "hole_d", 4.0))

    tab_finish = str(getattr(spec, "tab_finish", "metallic")).lower()

    scallop_d_mm = float(getattr(spec, "scallop_d_mm", 4.5))
    scallop_x_mm = float(getattr(spec, "scallop_x_mm", 8.0))

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
    body_x = tab_x + tab_w
    first_pin_x = body_x + body_w

    chamfer = draw_h * 0.12

    if tab_finish == "insulated":
        canvas.setFillColorRGB(0.12, 0.12, 0.12)
    else:
        canvas.setFillColorRGB(0.82, 0.82, 0.82)

    _draw_tab_with_side_chamfers(
        canvas,
        x=tab_x,
        y=y0,
        w=tab_w,
        h=draw_h,
        chamfer=chamfer,
        fill=1,
        stroke=0,
    )

    hole_r = (hole_d / width_mm) * draw_h * 0.5
    canvas.setFillColorRGB(1.0, 1.0, 1.0)
    canvas.circle(tab_x + tab_w * 0.5, cy, hole_r, fill=1, stroke=0)

    canvas.setFillColorRGB(0.12, 0.12, 0.12)
    canvas.rect(body_x, y0, body_w, draw_h, fill=1, stroke=0)

    scallop_r = (scallop_d_mm / width_mm) * draw_h * 0.5
    scallop_dx = (scallop_x_mm / (body_mm if body_mm > 0.0 else 1.0)) * body_w
    if scallop_dx < body_w * 0.10:
        scallop_dx = body_w * 0.10
    if scallop_dx > body_w * 0.90:
        scallop_dx = body_w * 0.90

    top_edge_y = y0 + draw_h
    bot_edge_y = y0

    canvas.setFillColorRGB(0.25, 0.25, 0.25)
    for edge_y in (top_edge_y, bot_edge_y):
        _draw_internal_semicircle(
            canvas,
            cx=body_x + scallop_dx,
            edge_y=edge_y,
            r=scallop_r,
            body_x=body_x,
            body_w=body_w,
            body_y=y0,
            body_h=draw_h,
        )

    canvas.setFillColorRGB(0.75, 0.75, 0.75)

    lead_th = draw_h * 0.07

    lead_step_fraction = 0.20
    lead_step_width_scale = 1.50
    lead_step_th_max_fraction_of_pitch = 0.75

    lead_step_len = lead_w * lead_step_fraction
    lead_step_th = lead_th * lead_step_width_scale

    if pin_count == 3:
        pitch_mm = float(getattr(spec, "pin_pitch_3_mm", 5.75))
    else:
        pitch_mm = float(getattr(spec, "pin_pitch_5_mm", 3.0))

    pitch = (pitch_mm / width_mm) * draw_h
    if pitch <= 0.0:
        pitch = draw_h * (0.18 if pin_count == 3 else 0.10)

    lead_step_th_max = pitch * lead_step_th_max_fraction_of_pitch
    if lead_step_th > lead_step_th_max:
        lead_step_th = lead_step_th_max

    offsets = compute_offsets(pin_count, pitch)

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
    label_mid = (pin_count - 1) / 2.0

    label_y_adjust: list[float] = []
    for i in range(pin_count):
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
