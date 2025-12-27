# file: fonts.py
from typing import List

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError


def load_font_family(argv: List[str]) -> str:
    """
    @brief Load a bold font and return the family name.

    Attempts Arial first, then Roboto if requested or Arial is
    unavailable.
    """
    font_family = "Arial Bold"
    use_roboto = "--roboto" in argv

    if use_roboto:
        _register_font("Roboto-Bold.ttf", font_family)
        return font_family

    for candidate in ["ArialBd.ttf", "Arial_Bold.ttf"]:
        try:
            _register_font(candidate, font_family)
            return font_family
        except TTFError:
            continue

    raise RuntimeError("Unable to load a suitable bold font.")


def _register_font(font_path: str, family_name: str) -> None:
    """@brief Register a TrueType font with ReportLab."""
    pdfmetrics.registerFont(TTFont(family_name, font_path))
