# file: src/packages/api.py

"""
@brief	Public package API for label renderers.
"""

from typing import Optional

from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect
from src.packages.resolve import resolve_package
from src.packages import registry as _registry


def format_package_for_text(raw: str) -> str:
    """
    @brief	Format a package string for printing on a label.

    @param raw	Raw package key
    @return	Canonical id (variant-aware) if known, else raw
    """
    resolved = resolve_package(raw)
    if resolved is None:
        return raw
    return resolved.print_id


def draw_package(
    canvas: Canvas,
    rect: simple_rect,
    raw_package: str,
    spec: Optional[object] = None,
) -> None:
    """
    @brief		Draw a package by resolving then dispatching.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param raw_package	Raw package string from label JSON
    @param spec		Optional device spec for pin labelling
    """
    if not raw_package:
        return

    resolved = resolve_package(raw_package)
    if resolved is None:
        return
    if not resolved.is_renderable:
        return
    if resolved.family_id is None:
        return

    drawer = _registry.FAMILY_DRAWERS.get(resolved.family_id)
    if drawer is None:
        return

    drawer(canvas, rect, resolved, spec)
