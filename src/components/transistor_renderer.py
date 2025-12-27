# file: src/components/transistor_renderer.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch

from src.layout.paper_layouts import paper_config_t
from src.layout.label_layout import (
    label_rect_t,
    label_layout_t,
    compute_label_layout,
)

from src.drawing.sticker_rect import sticker_rect_t
from src.model.devices import transistor_label_t

from src.core.markup import draw_markup
from src.core.geometry import simple_rect

from src.symbols.routing import resolve_transistor_drawer
from src.packages.api import draw_package

from src.components.label_renderer_base import (
    apply_standard_margins,
    draw_center_line,
    label_fonts,
)


def draw_transistor_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: transistor_label_t,
    font_family: str,
    draw_center: bool,
) -> None:
    """@brief Draw a complete transistor label (BJT, MOSFET, JFET, IGBT)."""

    with sticker_rect_t(canvas, layout, row, column) as rect:

        # Consistent margins
        apply_standard_margins(rect)

        # Optional guideline
        if draw_center:
            draw_center_line(canvas, rect)

        layout_info: label_layout_t = compute_label_layout(rect, symbol_fraction=0.33)
        text_rect: label_rect_t = layout_info.text
        symbol_rect: label_rect_t = layout_info.symbol

        # --------------------------------------------------
        # Schematic symbol (top right)
        # --------------------------------------------------
        drawer = resolve_transistor_drawer(label.subtype)

        big_symbol = simple_rect(
            symbol_rect.left,
            symbol_rect.bottom + symbol_rect.height * 0.40,
            symbol_rect.width,
            symbol_rect.height * 0.60,
        )
        drawer(canvas, big_symbol)

        # --------------------------------------------------
        # Package rendering (bottom right)
        # --------------------------------------------------
        if label.package:
            pkg_h = symbol_rect.height * 0.32
            pkg_box = simple_rect(
                symbol_rect.left + symbol_rect.width * 0.05,
                symbol_rect.bottom + symbol_rect.height * 0.05,
                symbol_rect.width * 0.90,
                pkg_h,
            )
            draw_package(canvas, pkg_box, label.package, label.spec)

        # --------------------------------------------------
        # Text block (left)
        # --------------------------------------------------
        specs = label.spec.format() if label.spec else []

        title_fs = label_fonts["title"]
        pkg_fs = label_fonts["meta"]
        spec_fs = label_fonts["spec"]

        total_h = title_fs * 0.9
        if label.package:
            total_h += pkg_fs * 1.1
        total_h += len(specs) * (spec_fs * 1.5)

        cursor_y = text_rect.bottom + (text_rect.height + total_h) / 2.0
        cursor_x = text_rect.left

        # Part number
        canvas.setFont(font_family, title_fs)
        canvas.drawString(cursor_x, cursor_y - title_fs, label.part_number)
        cursor_y -= title_fs * 1.2

        # Package text
        if label.package:
            from src.layout.label_text import format_package_for_text

            pkg_text = format_package_for_text(label.package)
            canvas.setFont(font_family, pkg_fs)
            canvas.drawString(cursor_x, cursor_y - pkg_fs, pkg_text)
            cursor_y -= pkg_fs * 1.5

        # Horizontal divider
        line_y = cursor_y
        canvas.setLineWidth(0.6)
        canvas.line(cursor_x, line_y, cursor_x + text_rect.width * 0.75, line_y)
        cursor_y -= spec_fs * 1.2

        # Specification output
        for line in specs:
            draw_markup(canvas, cursor_x, cursor_y, line, font_family, spec_fs)
            cursor_y -= spec_fs * 1.25
