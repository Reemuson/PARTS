# file: src/components/active_renderer.py

from reportlab.pdfgen.canvas import Canvas

from src.drawing.sticker_rect import sticker_rect_t
from src.layout.paper_layouts import paper_config_t
from src.model.devices import active_label_t

from src.components.label_renderer_base import (
    apply_standard_margins,
    label_fonts,
)


def draw_active_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: active_label_t,
    font_family: str,
) -> None:
    """@brief Draw a label for an active device."""

    with sticker_rect_t(canvas, layout, row, column) as rect:

        apply_standard_margins(rect)

        title_fs = label_fonts["title"]
        meta_fs = label_fonts["meta"]

        canvas.setFont(font_family, title_fs * 1.35)
        canvas.drawCentredString(
            rect.left + rect.width * 0.50,
            rect.bottom + rect.height * 0.60,
            label.part_number,
        )

        meta_line = _compose_meta_line(label)
        if meta_line:
            canvas.setFont(font_family, meta_fs * 1.35)
            canvas.drawCentredString(
                rect.left + rect.width * 0.50,
                rect.bottom + rect.height * 0.44,
                meta_line,
            )


def _compose_meta_line(label: active_label_t) -> str:
    """@brief Build compact info line such as 'NPN TO-92'."""
    parts = []
    if label.role:
        parts.append(label.role)
    if label.package:
        parts.append(label.package)
    return " ".join(parts)
