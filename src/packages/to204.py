# file: src/packages/to204.py

from __future__ import annotations

from dataclasses import dataclass
from math import acos, atan2, cos, degrees, radians, sin, sqrt, tan
from typing import List, Optional, Tuple

from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect

from src.packages.tht_helpers import (
    clamp_float,
    clamp_int,
    default_numeric_labels,
    draw_pin_with_ring,
    draw_radial_pin_label,
    linspace_angles_deg,
    parse_pin_config,
)


def _resolve_pin_labels(
    *,
    pin_count: int,
    spec: object | None,
    is_body_pin: bool,
) -> List[str]:
    """
    @brief		Resolve final pin labels with optional body-as-pin-1 support.
    @note		If is_body_pin is True then label[0] is the body label (pin 1) and
           		the lead pins map to label indices 1..pin_count (pins 2..N+1).
    @param pin_count	Number of lead pins
    @param spec		Optional spec providing pin_config or pin_labels
    @param is_body_pin	True if body is pin 1
    @return		Resolved label list
    """
    total_labels = pin_count + (1 if is_body_pin else 0)

    if spec is not None and getattr(spec, "pin_config", None):
        labels = parse_pin_config(getattr(spec, "pin_config"))
        return [str(x) for x in labels]

    if spec is not None and getattr(spec, "pin_labels", None):
        labels = getattr(spec, "pin_labels")
        return [str(x) for x in labels]

    labels = default_numeric_labels(total_labels)
    return [str(x) for x in labels]


@dataclass(frozen=True)
class to204_dims_t:
    """
    @brief	Physical dimensions for TO-204 (TO-3) underside.
    @note	All dimensions are in millimetres
    """

    body_tip_to_tip_mm: float = 38.80
    body_flat_to_flat_mm: float = 25.40

    body_corner_radius_mm: float = 4.40
    body_centre_arc_radius_mm: float = 11.4

    mount_hole_diameter_mm: float = 4.10
    mount_hole_pitch_mm: float = 25.40

    lead_count: int = 2
    lead_diameter_mm: float = 1.00


def _scale_mm_to_px(*, mm: float, ref_mm: float, ref_px: float) -> float:
    """
    @brief		Convert a millimetre dimension into local pixels using a reference.
    @param mm		Dimension in mm
    @param ref_mm	Reference mm matching ref_px
    @param ref_px	Reference pixels
    @return		Pixels
    """
    if ref_mm <= 0.0:
        return 0.0
    return (mm / ref_mm) * ref_px


def _v_sub(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """
    @brief	Vector subtraction a - b.
    @param a	Vector a
    @param b	Vector b
    @return	Result vector
    """
    return (a[0] - b[0], a[1] - b[1])


def _v_add(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """
    @brief	Vector addition a + b.
    @param a	Vector a
    @param b	Vector b
    @return	Result vector
    """
    return (a[0] + b[0], a[1] + b[1])


def _v_mul(a: Tuple[float, float], s: float) -> Tuple[float, float]:
    """
    @brief	Scalar multiply.
    @param a	Vector
    @param s	Scalar
    @return	Result vector
    """
    return (a[0] * s, a[1] * s)


def _v_len(a: Tuple[float, float]) -> float:
    """
    @brief	Vector length.
    @param a	Vector
    @return	Length
    """
    return sqrt((a[0] * a[0]) + (a[1] * a[1]))


def _v_unit(a: Tuple[float, float]) -> Tuple[float, float]:
    """
    @brief	Unit vector.
    @param a	Vector
    @return	Unit vector, or (0,0) if zero
    """
    l = _v_len(a)
    if l <= 1.0e-9:
        return (0.0, 0.0)
    return (a[0] / l, a[1] / l)


def _v_dot(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    @brief	Dot product.
    @param a	Vector a
    @param b	Vector b
    @return	Dot product
    """
    return (a[0] * a[0]) + (a[1] * b[1])


def _angle_deg_from_centre(
    centre: Tuple[float, float],
    point: Tuple[float, float],
) -> float:
    """
    @brief		Angle in degrees from centre to point.
    @param centre	Centre point
    @param point	Point on circle
    @return		Angle in degrees
    """
    return degrees(atan2(point[1] - centre[1], point[0] - centre[0]))


def _rotate_point_about_centre_90_deg(
    centre: Tuple[float, float],
    point: Tuple[float, float],
) -> Tuple[float, float]:
    """
    @brief		Rotate a point about centre by +90 degrees.
    @param centre	Rotation centre
    @param point	Point to rotate
    @return		Rotated point
    """
    dx = point[0] - centre[0]
    dy = point[1] - centre[1]
    return (centre[0] - dy, centre[1] + dx)


def _safe_corner_radius_for_diamond(
    *,
    tip_dx: float,
    tip_dy: float,
    requested_r: float,
) -> float:
    """
    @brief		Clamp corner radius to keep fillets inside the outline.
    @param tip_dx	Horizontal half extent in px
    @param tip_dy	Vertical half extent in px
    @param requested_r	Requested fillet radius in px
    @return		Safe fillet radius in px
    """
    if requested_r <= 0.0:
        return 0.0

    top = (0.0, tip_dy)
    right = (tip_dx, 0.0)
    bot = (0.0, -tip_dy)
    left = (-tip_dx, 0.0)
    pts = [top, right, bot, left]

    max_r = requested_r

    i = 0
    while i < 4:
        a = pts[i]
        b = pts[(i + 1) % 4]
        edge_len = _v_len(_v_sub(b, a))
        max_r = min(max_r, edge_len * 0.45)
        i += 1

    return clamp_float(max_r, 0.0, min(tip_dx, tip_dy) * 0.49)


def _fillet_arc_for_corner(
    prev_pt: Tuple[float, float],
    corner_pt: Tuple[float, float],
    next_pt: Tuple[float, float],
    radius: float,
) -> Optional[
    Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], float, float]
]:
    """
    @brief		Compute tangency points and arc parameters for a filleted corner.
    @param prev_pt	Previous vertex
    @param corner_pt	Corner vertex
    @param next_pt	Next vertex
    @param radius	Requested fillet radius in px
    @return		(t1, t2, centre, start_deg, extent_deg) or None
    """
    if radius <= 0.01:
        return None

    v_prev = _v_sub(prev_pt, corner_pt)
    v_next = _v_sub(next_pt, corner_pt)
    len_prev = _v_len(v_prev)
    len_next = _v_len(v_next)

    if (len_prev <= 1.0e-6) or (len_next <= 1.0e-6):
        return None

    v1 = _v_unit(v_prev)
    v2 = _v_unit(v_next)

    dot = clamp_float(_v_dot(v1, v2), -1.0, 1.0)
    phi = acos(dot)

    if phi <= radians(2.0):
        return None
    if phi >= radians(178.0):
        return None

    tan_half = tan(phi * 0.5)
    if abs(tan_half) <= 1.0e-6:
        return None

    max_t_dist = min(len_prev, len_next) * 0.49
    max_radius = max_t_dist * abs(tan_half)
    radius = clamp_float(radius, 0.0, max_radius)

    if radius <= 0.01:
        return None

    t_dist = radius / abs(tan_half)
    if t_dist >= max_t_dist:
        return None

    offset = radius / max(sin(phi * 0.5), 1.0e-6)
    bis = _v_unit(_v_add(v1, v2))
    centre = _v_add(corner_pt, _v_mul(bis, offset))

    t1 = _v_add(corner_pt, _v_mul(v1, t_dist))
    t2 = _v_add(corner_pt, _v_mul(v2, t_dist))

    start_deg = _angle_deg_from_centre(centre, t1)

    u1 = _v_sub(t1, centre)
    u2 = _v_sub(t2, centre)
    cross = (u1[0] * u2[1]) - (u1[1] * u2[0])
    dotp = (u1[0] * u2[0]) + (u1[1] * u2[1])

    extent = degrees(atan2(cross, dotp))
    if abs(extent) <= 0.1:
        return None

    return (t1, t2, centre, start_deg, extent)


def _path_arc_connected(
    path: object,
    *,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    start_deg: float,
    extent_deg: float,
) -> None:
    """
    @brief		Add an arc segment without breaking the current subpath.
    @param path		Path object from canvas.beginPath()
    @param x1		Arc bbox left
    @param y1		Arc bbox bottom
    @param x2		Arc bbox right
    @param y2		Arc bbox top
    @param start_deg	Start angle in degrees
    @param extent_deg	Sweep in degrees (signed)
    """
    arc_to = getattr(path, "arcTo", None)
    if callable(arc_to):
        arc_to(x1, y1, x2, y2, start_deg, extent_deg)
        return

    arc = getattr(path, "arc", None)
    if callable(arc):
        arc(x1, y1, x2, y2, start_deg, extent_deg)


def _arc_params_from_centre(
    *,
    arc_centre: Tuple[float, float],
    entry_pt: Tuple[float, float],
    exit_pt: Tuple[float, float],
) -> Tuple[float, float]:
    """
    @brief		Compute arc (start_deg, extent_deg) around a fixed centre.
    @param arc_centre	Arc centre
    @param entry_pt	Arc start point
    @param exit_pt	Arc end point
    @return		(start_deg, extent_deg)
    """
    start_deg = _angle_deg_from_centre(arc_centre, entry_pt)

    u1 = _v_sub(entry_pt, arc_centre)
    u2 = _v_sub(exit_pt, arc_centre)

    cross = (u1[0] * u2[1]) - (u1[1] * u2[0])
    dotp = (u1[0] * u2[0]) + (u1[1] * u2[1])

    return (start_deg, degrees(atan2(cross, dotp)))


def _tangent_points_from_external_point_to_circle(
    *,
    point: Tuple[float, float],
    circle_centre: Tuple[float, float],
    circle_r: float,
) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    @brief			Compute the two tangency points from an external point to a circle.
    @param point		External point
    @param circle_centre	Circle centre
    @param circle_r		Circle radius
    @return			(upper_tangent, lower_tangent) or None
    """
    px, py = point
    cx, cy = circle_centre
    r = float(circle_r)

    vx = px - cx
    vy = py - cy
    d = sqrt((vx * vx) + (vy * vy))

    if (r <= 1.0e-6) or (d <= (r + 1.0e-6)):
        return None

    ux = vx / d
    uy = vy / d

    alpha = acos(clamp_float(r / d, -1.0, 1.0))
    ca = cos(alpha)
    sa = sin(alpha)

    perp_x = -uy
    perp_y = ux

    tx1 = cx + r * ((ux * ca) + (perp_x * sa))
    ty1 = cy + r * ((uy * ca) + (perp_y * sa))

    tx2 = cx + r * ((ux * ca) - (perp_x * sa))
    ty2 = cy + r * ((uy * ca) - (perp_y * sa))

    p1 = (tx1, ty1)
    p2 = (tx2, ty2)

    if p1[1] >= p2[1]:
        return (p1, p2)

    return (p2, p1)


def _build_to3_outline_path(
    canvas: Canvas,
    *,
    cx: float,
    cy: float,
    tip_dx: float,
    tip_dy: float,
    variable_corner_r: float,
    centre_arc_r: float,
) -> object:
    """
    @brief			Build a TO-3 style outline with tangent side segments.
    @param canvas		ReportLab canvas
    @param cx			Centre x
    @param cy			Centre y
    @param tip_dx		Horizontal half extent in px
    @param tip_dy		Vertical half extent in px
    @param variable_corner_r	Side corner fillet radius in px
    @param centre_arc_r		Top/bottom arc radius in px
    @return			ReportLab path
    """
    centre = (cx, cy)

    top0 = (cx, cy + tip_dy)
    right0 = (cx + tip_dx, cy)
    bot0 = (cx, cy - tip_dy)
    left0 = (cx - tip_dx, cy)

    pts0: List[Tuple[float, float]] = [top0, right0, bot0, left0]

    pts: List[Tuple[float, float]] = []
    i = 0
    while i < 4:
        pts.append(_rotate_point_about_centre_90_deg(centre, pts0[i]))
        i += 1

    left_corner_pt = pts[0]
    right_corner_pt = pts[2]

    variable_corner_r = _safe_corner_radius_for_diamond(
        tip_dx=tip_dx,
        tip_dy=tip_dy,
        requested_r=variable_corner_r,
    )
    centre_arc_r = clamp_float(
        float(centre_arc_r),
        0.0,
        max(tip_dx, tip_dy) * 3.0,
    )

    left_tangents = _tangent_points_from_external_point_to_circle(
        point=left_corner_pt,
        circle_centre=centre,
        circle_r=centre_arc_r,
    )
    right_tangents = _tangent_points_from_external_point_to_circle(
        point=right_corner_pt,
        circle_centre=centre,
        circle_r=centre_arc_r,
    )
    if (left_tangents is None) or (right_tangents is None):
        path = canvas.beginPath()
        path.moveTo(left_corner_pt[0], left_corner_pt[1])
        path.lineTo(pts[1][0], pts[1][1])
        path.lineTo(right_corner_pt[0], right_corner_pt[1])
        path.lineTo(pts[3][0], pts[3][1])
        path.close()
        return path

    left_upper, left_lower = left_tangents
    right_upper, right_lower = right_tangents

    right_fillet = _fillet_arc_for_corner(
        right_upper,
        right_corner_pt,
        right_lower,
        variable_corner_r,
    )
    left_fillet = _fillet_arc_for_corner(
        left_lower,
        left_corner_pt,
        left_upper,
        variable_corner_r,
    )

    path = canvas.beginPath()

    path.moveTo(left_upper[0], left_upper[1])

    start_deg, extent_deg = _arc_params_from_centre(
        arc_centre=centre,
        entry_pt=left_upper,
        exit_pt=right_upper,
    )
    _path_arc_connected(
        path,
        x1=centre[0] - centre_arc_r,
        y1=centre[1] - centre_arc_r,
        x2=centre[0] + centre_arc_r,
        y2=centre[1] + centre_arc_r,
        start_deg=start_deg,
        extent_deg=extent_deg,
    )

    if right_fillet is None:
        path.lineTo(right_corner_pt[0], right_corner_pt[1])
    else:
        t1, t2, arc_centre, start_deg, extent_deg = right_fillet
        path.lineTo(t1[0], t1[1])
        _path_arc_connected(
            path,
            x1=arc_centre[0] - variable_corner_r,
            y1=arc_centre[1] - variable_corner_r,
            x2=arc_centre[0] + variable_corner_r,
            y2=arc_centre[1] + variable_corner_r,
            start_deg=start_deg,
            extent_deg=extent_deg,
        )
        path.lineTo(t2[0], t2[1])

    path.lineTo(right_lower[0], right_lower[1])

    start_deg, extent_deg = _arc_params_from_centre(
        arc_centre=centre,
        entry_pt=right_lower,
        exit_pt=left_lower,
    )
    _path_arc_connected(
        path,
        x1=centre[0] - centre_arc_r,
        y1=centre[1] - centre_arc_r,
        x2=centre[0] + centre_arc_r,
        y2=centre[1] + centre_arc_r,
        start_deg=start_deg,
        extent_deg=extent_deg,
    )

    if left_fillet is None:
        path.lineTo(left_corner_pt[0], left_corner_pt[1])
    else:
        t1, t2, arc_centre, start_deg, extent_deg = left_fillet
        path.lineTo(t1[0], t1[1])
        _path_arc_connected(
            path,
            x1=arc_centre[0] - variable_corner_r,
            y1=arc_centre[1] - variable_corner_r,
            x2=arc_centre[0] + variable_corner_r,
            y2=arc_centre[1] + variable_corner_r,
            start_deg=start_deg,
            extent_deg=extent_deg,
        )
        path.lineTo(t2[0], t2[1])

    path.lineTo(left_upper[0], left_upper[1])
    path.close()
    return path


def draw_to204_package(
    canvas: Canvas,
    rect: simple_rect,
    *,
    pin_count: int,
    pin_arc_start_deg: float,
    pin_arc_stop_deg: float,
    pin_diameter_mm: float,
    is_body_pin: bool = False,
    device_spec: object | None = None,
    dims: Optional[to204_dims_t] = None,
) -> None:
    """
    @brief			Draw TO-204 (TO-3) package underside view.
    @param canvas		ReportLab canvas
    @param rect			Target rectangle
    @param pin_count		Number of leads (1-15 supported)
    @param pin_arc_start_deg	Start angle for pin distribution
    @param pin_arc_stop_deg	Stop angle for pin distribution
    @param pin_diameter_mm	Pin diameter in mm
    @param is_body_pin		True if body is pin 1
    @param device_spec		Optional spec providing labels
    @param dims			Optional physical dims override
    """
    pin_count = clamp_int(int(pin_count), 1, 15)

    final_dims = dims if dims is not None else to204_dims_t()

    is_body_pin = bool(is_body_pin)

    final_labels = _resolve_pin_labels(
        pin_count=pin_count,
        spec=device_spec,
        is_body_pin=is_body_pin,
    )

    cx = rect.left + rect.width * 0.5
    cy = rect.bottom + rect.height * 0.5
    centre = (cx, cy)

    ref_px = min(rect.width, rect.height) * 1.75
    ref_mm = max(final_dims.body_tip_to_tip_mm, 1.0)

    tip_to_tip_px = _scale_mm_to_px(
        mm=final_dims.body_tip_to_tip_mm,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )
    flat_to_flat_px = _scale_mm_to_px(
        mm=final_dims.body_flat_to_flat_mm,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )

    variable_corner_r_px = _scale_mm_to_px(
        mm=final_dims.body_corner_radius_mm,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )
    centre_arc_r_px = _scale_mm_to_px(
        mm=final_dims.body_centre_arc_radius_mm,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )

    tip_dy = tip_to_tip_px * 0.5
    tip_dx = flat_to_flat_px * 0.5

    mount_hole_r = _scale_mm_to_px(
        mm=final_dims.mount_hole_diameter_mm * 0.5,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )
    mount_pitch = _scale_mm_to_px(
        mm=final_dims.mount_hole_pitch_mm,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )

    pin_diameter_mm = clamp_float(float(pin_diameter_mm), 0.6, 2.5)
    pin_r = _scale_mm_to_px(
        mm=pin_diameter_mm * 0.5,
        ref_mm=ref_mm,
        ref_px=ref_px,
    )
    pin_r = clamp_float(pin_r, ref_px * 0.012, ref_px * 0.06)

    canvas.saveState()

    base_path = _build_to3_outline_path(
        canvas,
        cx=cx,
        cy=cy,
        tip_dx=tip_dx,
        tip_dy=tip_dy,
        variable_corner_r=variable_corner_r_px,
        centre_arc_r=centre_arc_r_px,
    )

    canvas.setFillColorRGB(0.78, 0.77, 0.76)
    canvas.setStrokeColorRGB(0.68, 0.67, 0.66)
    canvas.setLineWidth(1.0)
    canvas.drawPath(base_path, stroke=1, fill=1)

    mount_top0 = (cx, cy + mount_pitch * 0.5)
    mount_bot0 = (cx, cy - mount_pitch * 0.5)

    mount_left = _rotate_point_about_centre_90_deg(centre, mount_top0)
    mount_right = _rotate_point_about_centre_90_deg(centre, mount_bot0)

    canvas.setFillColorRGB(1.0, 1.0, 1.0)
    canvas.circle(mount_left[0], mount_left[1], mount_hole_r, 0, 1)
    canvas.circle(mount_right[0], mount_right[1], mount_hole_r, 0, 1)

    angles = linspace_angles_deg(pin_count, pin_arc_start_deg, pin_arc_stop_deg)

    pin_ring_r = min(tip_dx, tip_dy) * 0.50
    pin_points: List[Tuple[float, float]] = []

    for a_deg in angles:
        a = radians(a_deg)
        px = cx + pin_ring_r * cos(a)
        py = cy + pin_ring_r * sin(a)
        pin_points.append((px, py))
        draw_pin_with_ring(
            canvas,
            x=px,
            y=py,
            pin_r=pin_r,
            ring_total_diameter_scale=4.0,
        )

    font_size = rect.height * 0.20
    font_size = clamp_float(font_size, rect.height * 0.08, rect.height * 0.16)

    canvas.setFont("Helvetica", font_size)
    canvas.setFillColorRGB(0.0, 0.0, 0.0)

    radial_pad = max(pin_r * 4.0, font_size * 1.1)

    if is_body_pin and len(final_labels) >= 1:
        body_label = str(final_labels[0]).upper()
        body_x = mount_right[0] - (mount_hole_r * 2.2)
        body_y = mount_right[1]
        canvas.drawRightString(body_x, body_y - (font_size * 0.35), body_label)

    label_index_offset = 1 if is_body_pin else 0

    i = 0
    while i < len(pin_points):
        label_index = i + label_index_offset
        if label_index >= len(final_labels):
            break

        label = str(final_labels[label_index]).upper()
        px, py = pin_points[i]

        draw_radial_pin_label(
            canvas,
            cx=cx,
            cy=cy,
            pin_x=px,
            pin_y=py,
            label=label,
            font_size=font_size,
            pad=radial_pad,
        )

        i += 1

    canvas.restoreState()
