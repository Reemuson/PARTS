# file: src/components/resistor_renderer.py

import math
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black
from reportlab.lib.units import inch

from src.drawing.sticker_rect import sticker_rect_t
from src.layout.paper_layouts import paper_config_t
from src.layout.label_layout import compute_label_layout, label_rect_t
from src.model.devices import resistor_label_t

from src.core.resistor_value import (
    resistor_value_t,
    get_3digit_code,
    get_4digit_code,
    get_eia98_code,
)

from src.packages.resistor_axial import draw_resistor_body

from src.components.label_renderer_base import (
    apply_standard_margins,
    label_fonts,
)


def draw_resistor_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: resistor_label_t,
    font_family: str,
) -> None:
    """@brief Draw a complete resistor label on the sheet."""

    with sticker_rect_t(canvas, layout, row, column) as rect:

        # Standardised margins
        apply_standard_margins(rect)

        layout_info = compute_label_layout(rect, symbol_fraction=None)
        box: label_rect_t = layout_info.usable

        rv = resistor_value_t(label.value_ohms)

        # ------------ TEXT ------------
        value_fs = label_fonts["title"]
        ohm_fs = label_fonts["title"]
        smd_fs = label_fonts["smd"]
        spacing = 3.0

        value = rv.format_value()
        ohm = "Ω"

        v_w = canvas.stringWidth(value, font_family, value_fs * 1.35)
        o_w = canvas.stringWidth(ohm, font_family, ohm_fs * 1.35)
        total = v_w + o_w + spacing

        x = box.left + box.width / 4 - total / 2
        y = box.bottom + box.height / 2 - value_fs / 2

        canvas.setFont(font_family, value_fs * 1.5)
        canvas.drawString(x, y, value)

        canvas.setFont(font_family, ohm_fs * 1.5)
        canvas.drawString(x + v_w + spacing, y, ohm)

        # ------------ BODY GRAPHICS ------------
        from reportlab.lib.colors import HexColor

        draw_resistor_body(
            canvas,
            rv,
            HexColor("#FFFFFB"),
            HexColor("#F2EFA3"),
            box.left + box.width / 2,
            box.bottom + box.height / 2 - box.height / 45,
            box.width / 3.5,
            box.height / 3.5,
            3,
        )

        draw_resistor_body(
            canvas,
            rv,
            HexColor("#F5FCFF"),
            HexColor("#77C1D3"),
            box.left + box.width * 0.75,
            box.bottom + box.height / 2 - box.height / 45,
            box.width / 3.5,
            box.height / 3.5,
            4,
        )

        # ------------ SMD CODES ------------
        canvas.setFont(font_family, smd_fs * 1.35)
        canvas.drawString(
            box.left + box.width / 2 + box.width / 32,
            box.bottom + box.height / 2.9,
            get_3digit_code(rv),
        )
        canvas.drawCentredString(
            box.left + box.width * 3 / 4,
            box.bottom + box.height / 2.9,
            get_4digit_code(rv),
        )
        canvas.drawRightString(
            box.left + box.width - box.width / 32,
            box.bottom + box.height / 2.9,
            get_eia98_code(rv),
        )
