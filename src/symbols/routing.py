# file: src/symbols/routing.py

from typing import Callable, Dict, Optional
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect
from src.symbols.diode import DIODE_DRAWERS
from src.symbols.transistor import TRANSISTOR_DRAWERS


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
}


# ------------------------------------------------------------
# Resolve diode symbol
# ------------------------------------------------------------
def resolve_diode_drawer(subtype: Optional[str]) -> symbol_drawer_t:
    table = _SYMBOL_REGISTRY["diode"]

    if not subtype:
        return table["standard"]

    key = subtype.strip().lower()
    return table.get(key, table["standard"])


# ------------------------------------------------------------
# Resolve transistor symbol
# ------------------------------------------------------------
def resolve_transistor_drawer(subtype: Optional[str]) -> symbol_drawer_t:
    table = _SYMBOL_REGISTRY["transistor"]

    if not subtype:
        return table["default"]

    key = subtype.strip().lower()
    return table.get(key, table["default"])
