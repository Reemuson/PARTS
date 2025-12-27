# file: src/components/capacitor_renderer.py

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black
from reportlab.lib.units import inch

from src.drawing.sticker_rect import sticker_rect_t
from src.layout.paper_layouts import paper_config_t
from src.model.devices import capacitor_label_t


def draw_capacitor_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: capacitor_label_t,
    font_family: str,
    draw_center_line: bool,
) -> None:
    """@brief Draw a complete capacitor label on the sheet."""
    with sticker_rect_t(canvas, layout, row, column) as rect:

        # Match unified margin
        rect.width -= 0.1 * inch
        rect.left += 0.05 * inch

        if draw_center_line:
            canvas.setStrokeColor(black, 0.25)
            canvas.setLineWidth(0.7)
            canvas.line(
                rect.left,
                rect.bottom + rect.height / 2.0,
                rect.left + rect.width,
                rect.bottom + rect.height / 2.0,
            )

        value_font = 0.16 * inch
        meta_font = 0.10 * inch

        # Main capacitance value
        canvas.setFont(font_family, value_font * 1.35)
        canvas.drawCentredString(
            rect.left + rect.width / 2.0,
            rect.bottom + rect.height * 0.60,
            label.value,
        )

        meta_line = _compose_meta_line(label)
        if meta_line:
            canvas.setFont(font_family, meta_font * 1.35)
            canvas.drawCentredString(
                rect.left + rect.width / 2.0,
                rect.bottom + rect.height * 0.44,
                meta_line,
            )


def _compose_meta_line(label: capacitor_label_t) -> str:
    """@brief Build a compact info line: voltage + dielectric."""
    parts = []
    if label.voltage:
        parts.append(label.voltage)
    if label.dielectric:
        parts.append(label.dielectric)
    return " ".join(parts)
