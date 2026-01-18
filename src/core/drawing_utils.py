# file: src/drawing/drawing_utils.py

from typing import Protocol

from reportlab.lib.colors import black, white
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics

from src.core.markup import draw_markup, measure_markup


class rect_like_t(Protocol):
    """
    @brief Minimal rectangle interface for drawing helpers.

    Any object with these attributes can be used:
    - left
    - bottom
    - width
    - height
    """

    left: float
    bottom: float
    width: float
    height: float


def draw_rounded_outline(
    canvas: Canvas,
    rect: rect_like_t,
    *,
    radius: float,
    line_width: float = 0.1,
) -> None:
    """
    @brief 		Draw a rounded rectangle outline matching a cell size.

    @param canvas     	ReportLab canvas to draw on.
    @param rect      	Rectangle providing left/bottom/width/height.
    @param radius     	Corner radius.
    @param line_width 	Outline thickness in points.
    """
    canvas.saveState()
    canvas.setStrokeColor(black, 0.5)
    canvas.setLineWidth(line_width)
    canvas.roundRect(
        rect.left,
        rect.bottom,
        rect.width,
        rect.height,
        radius,
    )
    canvas.restoreState()


def draw_arrow(
    canvas: Canvas, x1: float, y1: float, x2: float, y2: float, s: float
) -> None:
    from math import atan2, cos, sin

    canvas.setStrokeColor(black)
    canvas.setLineWidth(1.0)
    canvas.line(x1, y1, x2, y2)

    angle = atan2(y2 - y1, x2 - x1)
    head_len = 0.2 * s
    head_angle = 0.6

    ax1 = x2 - head_len * cos(angle - head_angle)
    ay1 = y2 - head_len * sin(angle - head_angle)
    ax2 = x2 - head_len * cos(angle + head_angle)
    ay2 = y2 - head_len * sin(angle + head_angle)

    p = canvas.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(ax1, ay1)
    p.lineTo(ax2, ay2)
    p.close()
    canvas.drawPath(p, stroke=1, fill=1)


def tri_path(canvas: Canvas, cx: float, cy: float, s: float, mirrored: bool = False):
    p = canvas.beginPath()
    if not mirrored:
        p.moveTo(cx - s, cy + s)
        p.lineTo(cx - s, cy - s)
        p.lineTo(cx + s, cy)
    else:
        p.moveTo(cx + s, cy + s)
        p.lineTo(cx + s, cy - s)
        p.lineTo(cx - s, cy)
    p.close()
    return p


def draw_cathode_bar(
    canvas: Canvas, cx: float, cy: float, s: float, mirrored: bool
) -> None:
    bar_x = cx + s if not mirrored else cx - s
    canvas.setLineWidth(1.6)
    canvas.line(bar_x, cy + s, bar_x, cy - s)


def draw_knockout_tag(
    canvas: Canvas,
    x: float,
    y: float,
    text: str,
    font: str,
    size: float,
) -> float:
    """
    @brief	Draw a knockout tag aligned to the caller's baseline.

    Text is drawn with draw_markup() so subscripts, superscripts,
    greek names and "+-" are handled consistently.

    @param canvas	Target canvas.
    @param x	Left x position.
    @param y	Baseline y position (same line as surrounding text).
    @param text	Text to draw (markup enabled).
    @param font	Font name.
    @param size	Font size (points).
    @return	Width consumed by the tag in points.
    """
    canvas.saveState()
    canvas.setFont(font, size)

    text_width = measure_markup(canvas, text, font, size)

    ascent = (pdfmetrics.getAscent(font) * size) / 1000.0
    descent = (abs(pdfmetrics.getDescent(font)) * size) / 1000.0

    padding_x = size * 0.22
    padding_y = size * 0.14

    optical_y = size * 0.07

    box_left = x
    box_bottom = y - descent - padding_y + optical_y
    box_width = text_width + (2.0 * padding_x)
    box_height = ascent + descent + (2.0 * padding_y)

    canvas.setFillColor(black)
    canvas.rect(
        box_left,
        box_bottom,
        box_width,
        box_height,
        stroke=0,
        fill=1,
    )

    canvas.setFillColor(white)
    draw_markup(
        canvas,
        x + padding_x,
        y,
        text,
        font,
        size,
    )

    canvas.restoreState()
    return box_width
