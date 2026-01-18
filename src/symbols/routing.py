# file: src/symbols/routing.py

"""
@brief	Symbol drawer routing and subtype resolution.
"""

from typing import Callable, Dict, Optional
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect
from src.symbols.diode import DIODE_DRAWERS
from src.symbols.transistor import TRANSISTOR_DRAWERS
from src.symbols.capacitor import CAPACITOR_DRAWERS


# ------------------------------------------------------------
# Type alias for symbol drawer
# ------------------------------------------------------------
symbol_drawer_t = Callable[[Canvas, simple_rect, Optional[str]], None]


# ------------------------------------------------------------
# Symbol registry
# ------------------------------------------------------------
_SYMBOL_REGISTRY: Dict[str, Dict[str, symbol_drawer_t]] = {
    "diode": DIODE_DRAWERS,
    "transistor": TRANSISTOR_DRAWERS,
    "capacitor": CAPACITOR_DRAWERS,
}


def resolve_diode_drawer(subtype: Optional[str]) -> symbol_drawer_t:
    """
    @brief		Resolve diode symbol drawer for a given subtype.
    @param subtype	Diode subtype string.
    @return		Callable symbol drawer.
    """
    table = _SYMBOL_REGISTRY["diode"]

    if not subtype:
        return table["standard"]

    key = subtype.strip().lower()
    return table.get(key, table["standard"])


def resolve_transistor_drawer(subtype: Optional[str]) -> symbol_drawer_t:
    """
    @brief		Resolve transistor symbol drawer for a given subtype.
    @param subtype	Transistor subtype string.
    @return		Callable symbol drawer.
    """
    table = _SYMBOL_REGISTRY["transistor"]

    if not subtype:
        return table["default"]

    key = subtype.strip().lower()
    return table.get(key, table["default"])


def resolve_capacitor_drawer(subtype: Optional[str]) -> symbol_drawer_t:
    """
    @brief		Resolve capacitor symbol drawer for a given subtype.
    @param subtype	Capacitor subtype string.
    @return		Callable symbol drawer.
    """
    table = _SYMBOL_REGISTRY["capacitor"]

    if not subtype:
        return table["standard"]

    key = subtype.strip().lower()
    return table.get(key, table["standard"])
