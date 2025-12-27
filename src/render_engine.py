# file: src/render_engine.py

from typing import Optional, List

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black

from src.layout.paper_layouts import paper_config_t
from src.drawing.sticker_rect import sticker_rect_t

from src.model.devices import (
    label_t,
    resistor_label_t,
    diode_label_t,
    capacitor_label_t,
    active_label_t,
    transistor_label_t,
)

from src.components.resistor_renderer import draw_resistor_label
from src.components.diode_renderer import draw_diode_label
from src.components.capacitor_renderer import draw_capacitor_label
from src.components.active_renderer import draw_active_label
from src.components.transistor_renderer import draw_transistor_label

from src.config.config_loader import render_options_t


# ======================================================================
# PAGE CONTROL
# ======================================================================


def begin_page(
    canvas: Canvas,
    layout: paper_config_t,
    draw_outlines: bool,
) -> None:
    if draw_outlines:
        _draw_outlines(canvas, layout)


def end_page(canvas: Canvas) -> None:
    canvas.showPage()


# ======================================================================
# MAIN ENTRY
# ======================================================================


def render_labels(
    canvas: Canvas,
    layout: paper_config_t,
    labels: List[Optional[label_t]],
    options: render_options_t,
    font_family: str,
) -> None:

    cols = layout.num_stickers_horizontal
    rows = layout.num_stickers_vertical
    per_page = cols * rows

    canvas.setTitle(f"Component Labels - {layout.paper_name}")
    begin_page(canvas, layout, options.draw_outlines)

    for position, label in enumerate(labels):

        row = (position // cols) % rows
        col = position % cols

        if position > 0 and row == 0 and col == 0:
            end_page(canvas)
            begin_page(canvas, layout, options.draw_outlines)

        if label is None:
            continue

        _draw_single_label(
            canvas,
            layout,
            row,
            col,
            label,
            options,
            font_family,
        )

    end_page(canvas)


# ======================================================================
# LABEL DISPATCH
# ======================================================================


def _draw_single_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: label_t,
    options: render_options_t,
    font_family: str,
) -> None:

    # -------- RESISTOR --------
    if isinstance(label, resistor_label_t):
        draw_resistor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
            options.draw_center_line,
        )
        return

    # -------- DIODE --------
    if isinstance(label, diode_label_t):
        draw_diode_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
            options.draw_center_line,
        )
        return

    # -------- CAPACITOR --------
    if isinstance(label, capacitor_label_t):
        draw_capacitor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
            options.draw_center_line,
        )
        return

    # -------- TRANSISTOR --------
    if isinstance(label, transistor_label_t):
        draw_transistor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
            options.draw_center_line,
        )
        return

    # -------- ACTIVE --------
    if isinstance(label, active_label_t):
        draw_active_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
            options.draw_center_line,
        )
        return


# ======================================================================
# OPTIONAL OUTLINES
# ======================================================================


def _draw_outlines(canvas: Canvas, layout: paper_config_t) -> None:
    for row in range(layout.num_stickers_vertical):
        for col in range(layout.num_stickers_horizontal):
            with sticker_rect_t(canvas, layout, row, col) as rect:
                canvas.setStrokeColor(black, 0.5)
                canvas.setLineWidth(0.1)
                canvas.roundRect(
                    rect.left,
                    rect.bottom,
                    rect.width,
                    rect.height,
                    rect.corner,
                )
