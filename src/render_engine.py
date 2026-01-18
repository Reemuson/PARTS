# file: src/render_engine.py

"""
@brief	Label rendering orchestration and page control.
"""

from dataclasses import dataclass
from typing import List, Optional

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.components.active_renderer import draw_active_label
from src.components.capacitor_renderer import draw_capacitor_label
from src.components.diode_renderer import draw_diode_label
from src.components.resistor_renderer import draw_resistor_label
from src.components.transistor_renderer import draw_transistor_label
from src.config.config_loader import render_options_t
from src.core.errors import render_error_t
from src.drawing.sticker_rect import sticker_rect_t
from src.layout.paper_layouts import paper_config_t
from src.model.devices import (
    active_label_t,
    capacitor_label_t,
    diode_label_t,
    label_t,
    resistor_label_t,
    transistor_label_t,
)


@dataclass(frozen=True)
class render_counts_t:
    """
    @brief	Internal counters for render progress.
    """

    labels_rendered: int
    pages_rendered: int


def render_labels(
    canvas: Canvas,
    layout: paper_config_t,
    labels: List[Optional[label_t]],
    options: render_options_t,
    font_family: str,
) -> render_counts_t:
    """
    @brief		Render labels onto a PDF canvas.
    @param canvas	ReportLab canvas to draw into.
    @param layout	Label sheet layout definition.
    @param labels	Label list, with None entries for blanks.
    @param options	Render options.
    @param font_family	Resolved font family identifier.
    @return		Render count summary.
    """
    cols = int(layout.num_stickers_horizontal)
    rows = int(layout.num_stickers_vertical)

    labels_rendered = 0
    pages_rendered = 1

    canvas.setTitle(f"Component Labels - {layout.paper_name}")
    _begin_page(canvas, layout, bool(options.draw_outlines))

    for position, label in enumerate(labels):
        row = (position // cols) % rows
        col = position % cols

        if position > 0 and row == 0 and col == 0:
            _end_page(canvas)
            pages_rendered += 1
            _begin_page(canvas, layout, bool(options.draw_outlines))

        if label is None:
            continue

        _draw_single_label(
            canvas,
            layout,
            int(row),
            int(col),
            label,
            options,
            font_family,
        )
        labels_rendered += 1

    _end_page(canvas)

    return render_counts_t(
        labels_rendered=int(labels_rendered),
        pages_rendered=int(pages_rendered),
    )


def _draw_single_label(
    canvas: Canvas,
    layout: paper_config_t,
    row: int,
    column: int,
    label: label_t,
    options: render_options_t,
    font_family: str,
) -> None:
    """
    @brief		Draw a single label at the given grid position.
    @param canvas	Target canvas.
    @param layout	Paper layout definition.
    @param row		Row index.
    @param column	Column index.
    @param label	Label model.
    @param options	Render options.
    @param font_family	Resolved font family identifier.
    @return		None.
    @warning		Raises render_error_t on unknown label types.
    """

    if isinstance(label, resistor_label_t):
        draw_resistor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
        )
        return

    if isinstance(label, diode_label_t):
        draw_diode_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
        )
        return

    if isinstance(label, capacitor_label_t):
        draw_capacitor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
        )
        return

    if isinstance(label, transistor_label_t):
        draw_transistor_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
        )
        return

    if isinstance(label, active_label_t):
        draw_active_label(
            canvas,
            layout,
            row,
            column,
            label,
            font_family,
        )
        return

    raise render_error_t(
        "Unknown label type",
        detail=str(type(label)),
    )


def _begin_page(
    canvas: Canvas,
    layout: paper_config_t,
    draw_outlines: bool,
) -> None:
    """
    @brief			Begin a page and draw any page-level adornments.
    @param canvas		Target canvas.
    @param layout		Paper layout definition.
    @param draw_outlines	Whether outlines should be drawn.
    @return			None.
    """
    if draw_outlines:
        _draw_outlines(canvas, layout)


def _end_page(canvas: Canvas) -> None:
    """
    @brief		End the current page and advance the canvas.
    @param canvas	Target canvas.
    @return		None.
    """
    canvas.showPage()


def _draw_outlines(canvas: Canvas, layout: paper_config_t) -> None:
    """
    @brief		Draw per-sticker outlines for debugging and alignment.
    @param canvas	Target canvas.
    @param layout	Paper layout definition.
    @return		None.
    """
    for row in range(int(layout.num_stickers_vertical)):
        for col in range(int(layout.num_stickers_horizontal)):
            with sticker_rect_t(canvas, layout, int(row), int(col)) as rect:
                canvas.setStrokeColor(black, 0.5)
                canvas.setLineWidth(0.1)
                canvas.roundRect(
                    rect.left,
                    rect.bottom,
                    rect.width,
                    rect.height,
                    rect.corner,
                )
