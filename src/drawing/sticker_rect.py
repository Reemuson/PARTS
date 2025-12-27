# file: src/drawing/sticker_rect.py

from typing import Iterator, Tuple

from reportlab.pdfgen.canvas import Canvas

from src.layout.paper_layouts import paper_config_t


class sticker_rect_t:
    """
    @brief	Context manager for drawing into a single sticker cell.

    @note	This object does not modify canvas state, it just exposes the
            computed rectangle fields for the requested (row, column).
    """

    def __init__(
        self,
        canvas: Canvas,
        layout: paper_config_t,
        row: int,
        column: int,
    ) -> None:
        """
        @brief	Compute the sticker rectangle for a given row and column.
        @param canvas	ReportLab canvas.
        @param layout	Paper layout configuration.
        @param row		Row index (0 = top row).
        @param column	Column index (0 = left column).
        @return			None.
        """
        self.left = float(layout.left_margin) + (
            float(layout.horizontal_stride) * float(column)
        )
        self.bottom = float(layout.pagesize[1]) - (
            float(layout.sticker_height)
            + float(layout.top_margin)
            + (float(layout.vertical_stride) * float(row))
        )
        self.width = float(layout.sticker_width)
        self.height = float(layout.sticker_height)
        self.corner = float(layout.sticker_corner_radius)
        self._canvas = canvas

    def __enter__(self) -> "sticker_rect_t":
        """
        @brief	Enter the sticker rectangle context.
        @return	The sticker rectangle.
        """
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        tb: object,
    ) -> bool:
        """
        @brief			Exit the sticker rectangle context.
        @param exc_type	Exception type, if any.
        @param exc		Exception instance, if any.
        @param tb		Traceback, if any.
        @return			False to propagate exceptions.
        """
        return False


def sticker_cells(
    layout: paper_config_t,
) -> Iterator[Tuple[int, int, int]]:
    """
    @brief			Enumerate sticker positions row by row.
    @param layout	Paper layout configuration.
    @return			Iterator yielding (position, row_index, column_index).
    """
    position = 0
    for row_index in range(layout.num_stickers_vertical):
        for column_index in range(layout.num_stickers_horizontal):
            yield position, row_index, column_index
            position += 1
