# file: src/packages/registry.py

from types import SimpleNamespace
from typing import Callable, Dict, Optional

from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect
from src.packages.model import resolved_package_t

from src.packages.diode_axial import draw_axial_package

from src.packages.capacitor_disc import draw_capacitor_disc

from src.packages.to92 import draw_to92_package
from src.packages.to204 import draw_to204_package
from src.packages.to205 import draw_to205_package
from src.packages.to206 import draw_to206_package
from src.packages.to218 import draw_to218_package
from src.packages.to220 import draw_to220_package
from src.packages.to225 import draw_to225_package
from src.packages.to243 import draw_to243_package
from src.packages.to247 import draw_to247_package
from src.packages.to264 import draw_to264_package
from src.packages.smd2 import draw_smd2_package
from src.packages.smd3 import draw_smd3_package
from src.packages.smd4 import draw_smd4_package

from src.packages.led_tht import draw_led_tht


drawer_fn_t = Callable[
    [Canvas, simple_rect, resolved_package_t, Optional[object]],
    None,
]

FAMILY_DRAWERS: Dict[str, drawer_fn_t] = {}


def register_family(family_id: str, drawer: drawer_fn_t) -> None:
    """
    @brief		Register a renderer family drawer function.

    @param family_id	Family identifier
    @param drawer	Drawer function
    """
    if family_id:
        FAMILY_DRAWERS[family_id] = drawer


def _merge_package_and_device_spec(
    pkg: resolved_package_t,
    device_spec: Optional[object],
) -> object:
    """
    @brief		Create an attribute object from package params + device pin metadata.

    @note		Only use this for drawers that expect a generic attribute object.

    @param pkg		Resolved package (params are mechanical)
    @param device_spec	Optional device spec (pin_config etc)
    @return		Attribute object suitable for legacy package drawers
    """
    ns = SimpleNamespace(**pkg.params)
    if device_spec is None:
        return ns

    pin_config = getattr(device_spec, "pin_config", None)
    if pin_config is not None:
        setattr(ns, "pin_config", pin_config)

    pin_labels = getattr(device_spec, "pin_labels", None)
    if pin_labels is not None:
        setattr(ns, "pin_labels", pin_labels)

    return ns


def _is_bidirectional_tvs(spec: Optional[object]) -> bool:
    """
    @brief	Detect whether a diode spec represents a bidirectional TVS.

    @param spec	Optional device spec.
    @return	True if spec indicates a bidirectional TVS.
    """
    if spec is None:
        return False

    subtype = getattr(spec, "subtype", None)
    if subtype is None:
        return False

    subtype_text = str(subtype).strip().lower()
    if subtype_text == "":
        return False

    if "tvs" not in subtype_text:
        return False

    return ("bi" in subtype_text) or ("bidirectional" in subtype_text)


def _draw_axial_round_body(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw axial round-body packages.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    material = str(pkg.params.get("material", ""))

    show_polarity_band = not _is_bidirectional_tvs(spec)

    draw_axial_package(
        canvas,
        rect,
        pkg.params,
        material,
        show_labels=True,
        show_polarity_band=show_polarity_band,
    )


def _draw_melf(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw MELF-style SMD cylindrical packages.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    params = dict(pkg.params)
    params["mount"] = "smd"

    material = str(params.get("material", ""))

    show_polarity_band = not _is_bidirectional_tvs(spec)

    draw_axial_package(
        canvas,
        rect,
        params,
        material,
        show_labels=True,
        show_polarity_band=show_polarity_band,
    )


def _draw_capacitor_disc(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw disc ceramic capacitor package.

    @param canvas	ReportLab canvas.
    @param rect		Target rectangle.
    @param pkg		Resolved package.
    @param spec		Optional device spec.
    @return		None.
    """
    draw_capacitor_disc(canvas, rect, pkg, spec)


def _draw_to92_moulded(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-92 moulded package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to92_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to204_diamond(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-204 diamond-base package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    @return		None
    """
    pin_count = int(pkg.params.get("pin_count", 2))
    start_deg = float(pkg.params.get("pin_arc_start_deg", -55.0))
    stop_deg = float(pkg.params.get("pin_arc_stop_deg", 55.0))
    pin_diameter_mm = float(pkg.params.get("pin_diameter_mm", 1.2))
    is_body_pin = bool(pkg.params.get("is_body_pin", False))

    draw_to204_package(
        canvas,
        rect,
        pin_count=pin_count,
        pin_arc_start_deg=start_deg,
        pin_arc_stop_deg=stop_deg,
        pin_diameter_mm=pin_diameter_mm,
        is_body_pin=is_body_pin,
        device_spec=spec,
    )


def _draw_to205_package(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-205 package.
    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to205_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to206_package(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-206 package.
    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to206_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to218_tab(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-218 tabbed package.
    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 2))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to218_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to220_tab(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-220 tabbed package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to220_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to225_tab(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-225 tabbed package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to225_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to243_tab(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-243 tabbed package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    @return		None
    """
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to243_package(canvas, rect, pkg.params, spec=merged)


def _draw_to247_tab(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw TO-247 tabbed package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to247_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_to264_body(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    pin_count = int(pkg.params.get("pin_count", 3))
    merged = _merge_package_and_device_spec(pkg, spec)
    draw_to264_package(canvas, rect, pin_count=pin_count, spec=merged)


def _draw_smd_2pad(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw 2-pad SMD package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    draw_smd2_package(
        canvas,
        rect,
        pkg.params,
        default_pin_labels=pkg.params.get("pin_labels"),
        spec=spec,
    )


def _draw_smd_3lead(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw 3-lead SMD package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    draw_smd3_package(
        canvas,
        rect,
        pkg.params,
        default_pin_labels=pkg.params.get("pin_labels"),
        spec=spec,
    )


def _draw_smd_4lead(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw 4-lead SMD package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    draw_smd4_package(
        canvas,
        rect,
        pkg.params,
        default_pin_labels=pkg.params.get("pin_labels"),
        spec=spec,
    )


def _draw_led_tht_round(
    canvas: Canvas,
    rect: simple_rect,
    pkg: resolved_package_t,
    spec: Optional[object],
) -> None:
    """
    @brief		Draw THT LED package.

    @param canvas	ReportLab canvas
    @param rect		Target rectangle
    @param pkg		Resolved package
    @param spec		Optional device spec
    """
    draw_led_tht(canvas, rect, pkg.params, spec)


register_family("axial_round_body", _draw_axial_round_body)
register_family("melf", _draw_melf)

register_family("capacitor_disc", _draw_capacitor_disc)

register_family("to92_moulded", _draw_to92_moulded)
register_family("to204_diamond", _draw_to204_diamond)
register_family("to205_package", _draw_to205_package)
register_family("to206_package", _draw_to206_package)
register_family("to218_tab", _draw_to218_tab)
register_family("to220_tab", _draw_to220_tab)
register_family("to225_tab", _draw_to225_tab)
register_family("to243_tab", _draw_to243_tab)
register_family("to247_tab", _draw_to247_tab)
register_family("to264_body", _draw_to264_body)
register_family("smd_2pad", _draw_smd_2pad)
register_family("smd_3lead", _draw_smd_3lead)
register_family("smd_4lead", _draw_smd_4lead)
register_family("led_tht_round", _draw_led_tht_round)
