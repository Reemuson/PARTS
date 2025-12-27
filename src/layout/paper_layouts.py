# file: paper_layouts.py
#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Tuple, Dict

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import inch, mm


@dataclass
class paper_config_t:
	"""
	@brief Configuration for a label sheet layout.

	Attributes describe a single sticker geometry and placement grid on
	a specific paper size.
	"""

	paper_name: str
	pagesize: Tuple[float, float]
	sticker_width: float
	sticker_height: float
	sticker_corner_radius: float
	left_margin: float
	top_margin: float
	horizontal_stride: float
	vertical_stride: float
	num_stickers_horizontal: int
	num_stickers_vertical: int


AVERY_5260 = paper_config_t(
	paper_name="AVERY_5260",
	pagesize=LETTER,
	sticker_width=(2 + 5 / 8) * inch,
	sticker_height=1 * inch,
	sticker_corner_radius=0.1 * inch,
	left_margin=3 / 16 * inch,
	top_margin=0.5 * inch,
	horizontal_stride=(2 + 6 / 8) * inch,
	vertical_stride=1 * inch,
	num_stickers_horizontal=3,
	num_stickers_vertical=10,
)

AVERY_L7157 = paper_config_t(
	paper_name="AVERY_L7157",
	pagesize=A4,
	sticker_width=64 * mm,
	sticker_height=24.3 * mm,
	sticker_corner_radius=3 * mm,
	left_margin=6.4 * mm,
	top_margin=14.1 * mm,
	horizontal_stride=66.552 * mm,
	vertical_stride=24.3 * mm,
	num_stickers_horizontal=3,
	num_stickers_vertical=11,
)

AVERY_L7144 = paper_config_t(
	paper_name="AVERY_L7144",
	pagesize=A4,
	sticker_width=38.1 * mm,
	sticker_height=21.2 * mm,
	sticker_corner_radius=3 * mm,
	left_margin=4.4 * mm,
	top_margin=11.4 * mm,
	horizontal_stride=40.5 * mm,
	vertical_stride=21.2 * mm,
	num_stickers_horizontal=5,
	num_stickers_vertical=13,
)

EJ_RANGE_24 = paper_config_t(
	paper_name="EJ_RANGE_24",
	pagesize=A4,
	sticker_width=63.5 * mm,
	sticker_height=33.9 * mm,
	sticker_corner_radius=2 * mm,
	left_margin=6.5 * mm,
	top_margin=13.2 * mm,
	horizontal_stride=66.45 * mm,
	vertical_stride=33.9 * mm,
	num_stickers_horizontal=3,
	num_stickers_vertical=8,
)


def get_paper_layouts() -> Dict[str, paper_config_t]:
	"""@brief Return all known paper layouts keyed by name."""
	return {
		AVERY_5260.paper_name: AVERY_5260,
		AVERY_L7157.paper_name: AVERY_L7157,
		AVERY_L7144.paper_name: AVERY_L7144,
		EJ_RANGE_24.paper_name: EJ_RANGE_24,
	}
