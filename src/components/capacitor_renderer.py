# file: src/components/capacitor_renderer.py

from reportlab.pdfgen.canvas import Canvas

from src.layout.paper_layouts import paper_config_t
from src.layout.label_layout import (
    label_rect_t,
    label_layout_t,
    compute_label_layout,
)

from src.drawing.sticker_rect import sticker_rect_t
from src.model.devices import capacitor_label_t

from src.core.markup import draw_markup
from src.core.geometry import simple_rect
from src.core.drawing_utils import draw_knockout_tag

from src.symbols.routing import resolve_capacitor_drawer
from src.packages.api import draw_package

from src.components.label_renderer_base import (
    apply_standard_margins,
    label_fonts,
)


def draw_capacitor_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: capacitor_label_t,
    font_family: str,
) -> None:
    """@brief Draw a complete capacitor label."""
    with sticker_rect_t(canvas, layout, row, column) as rect:

        # Consistent margins
        apply_standard_margins(rect)

        layout_info: label_layout_t = compute_label_layout(rect, symbol_fraction=0.33)
        text_rect: label_rect_t = layout_info.text
        symbol_rect: label_rect_t = layout_info.symbol

        # --------------------------------------------------
        # Schematic symbol (top right)
        # --------------------------------------------------
        drawer = resolve_capacitor_drawer(label.subtype)

        big_symbol = simple_rect(
            symbol_rect.left,
            symbol_rect.bottom + (symbol_rect.height * 0.40),
            symbol_rect.width,
            symbol_rect.height * 0.60,
        )
        drawer(canvas, big_symbol, label.subtype)

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
        meta_fs = label_fonts["meta"]
        spec_fs = label_fonts["spec"]

        total_h = title_fs * 0.9
        if label.package:
            total_h += meta_fs * 1.1
        total_h += len(specs) * (spec_fs * 1.5)

        cursor_y = text_rect.bottom + (text_rect.height + total_h) / 2.0
        cursor_x = text_rect.left

        # Part number
        canvas.setFont(font_family, title_fs)
        canvas.drawString(cursor_x, cursor_y - title_fs, label.part_number)
        cursor_y -= title_fs * 1.2

        # Subtype text
        subtype_text, dielectric = _resolve_meta_parts(label)

        canvas.setFont(font_family, meta_fs)
        canvas.drawString(cursor_x, cursor_y - meta_fs, subtype_text)

        meta_advance = canvas.stringWidth(subtype_text, font_family, meta_fs)
        if dielectric:
            meta_advance += meta_fs * 0.55
            draw_knockout_tag(
                canvas,
                cursor_x + meta_advance,
                cursor_y - meta_fs,
                dielectric,
                font_family,
                meta_fs * 0.92,
            )

        cursor_y -= meta_fs * 1.5

        # Horizontal divider
        line_y = cursor_y
        canvas.setLineWidth(0.6)
        canvas.line(cursor_x, line_y, cursor_x + (text_rect.width * 0.75), line_y)
        cursor_y -= spec_fs * 1.2

        # Specification output
        for line in specs:
            if _is_capacitance_line(line):
                cursor_y = _draw_capacitance_with_tolerance(
                    canvas,
                    cursor_x,
                    cursor_y,
                    line,
                    label,
                    font_family,
                    spec_fs,
                )
                continue

            draw_markup(canvas, cursor_x, cursor_y, line, font_family, spec_fs)
            cursor_y -= spec_fs * 1.25


def _resolve_meta_parts(label: capacitor_label_t) -> tuple[str, str | None]:
    """
    @brief		Resolve subtype text and optional dielectric tag.
    @param label	Capacitor label model.
    @return		(subtype_text, dielectric_tag)
    """
    subtype_raw = str(getattr(label, "subtype", "")).strip().lower()
    if not subtype_raw:
        return ("Capacitor", None)

    subtype = subtype_raw.capitalize()

    if (subtype_raw in ("ceramic", "monolithic", "film")) and label.spec is not None:
        dielectric = getattr(label.spec, "dielectric", None)
        if dielectric:
            return (subtype, str(dielectric))

    return (subtype, None)


def _is_capacitance_line(line: str) -> bool:
    """
    @brief		Check if a formatted spec line is the capacitance headline.
    @param line		Formatted spec line.
    @return		True if capacitance line.
    """
    return line.strip().startswith("C = ")


def _extract_capacitance_value(line: str) -> str:
    """
    @brief		Extract capacitance value from a 'C = ...' spec line.
    @param line		Formatted spec line.
    @return		Value string, may be empty.
    """
    text = line.strip()
    if not text.startswith("C = "):
        return ""
    return text[len("C = ") :].strip()


def _draw_capacitance_with_tolerance(
    canvas: Canvas,
    x: float,
    y: float,
    c_line: str,
    label: capacitor_label_t,
    font_family: str,
    size: float,
) -> float:
    """
    @brief	        Draw 'C = value' plus a knockout tolerance tag on the same line.
    @param canvas	Target canvas.
    @param x	        Left x position.
    @param y	        Baseline y position.
    @param c_line	Formatted capacitance spec line.
    @param label	Capacitor label model.
    @param font_family	Font family.
    @param size	        Font size.
    @return	        Next baseline y position after drawing.
    """
    c_value = _extract_capacitance_value(c_line)

    canvas.setFont(font_family, size)
    left_text = f"C = {c_value}"
    canvas.drawString(x, y, left_text)

    advance = canvas.stringWidth(left_text, font_family, size)

    tol = None
    if label.spec is not None:
        tol = getattr(label.spec, "tol", None)

    if tol:
        advance += size * 0.55
        draw_knockout_tag(
            canvas,
            x + advance,
            y,
            f"{tol}",
            font_family,
            size * 0.92,
        )

    return y - (size * 1.25)
