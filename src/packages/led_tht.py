# file: src/packages/led_tht.py

from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

from src.core.geometry import simple_rect, scale_physical
from src.core.colour import wavelength_to_rgb

PACKAGE_SCALE = 2.0


def draw_led_tht(
    canvas: Canvas,
    rect: simple_rect,
    info: dict,
    spec: object | None = None,
) -> None:

    # -----------------------------------------------------------------
    # Extract physical parameters from PACKAGE_DB
    # -----------------------------------------------------------------
    diam_mm = float(info.get("body_d", 5.0))
    body_h_mm = float(info.get("body_h", 8.5))
    lead_len_mm = float(info.get("lead_len", 20.0))
    lead_pitch_mm = float(info.get("lead_pitch", 2.54))
    lead_w_mm = float(info.get("lead_w", 0.6))

    # -----------------------------------------------------------------
    # Extract LED electrical/optical parameters from spec
    # -----------------------------------------------------------------
    wavelength = None
    lens = "diffused"

    if spec is not None:
        wavelength = getattr(spec, "wavelength", None)
        lens = getattr(spec, "lens", lens) or lens
        lens = lens.lower()

    # Resolve LED colour
    if wavelength:
        r, g, b = wavelength_to_rgb(wavelength)
    else:
        r, g, b = (0.80, 0.80, 0.80)  # fallback grey

    # -----------------------------------------------------------------
    # Scaling
    # -----------------------------------------------------------------
    bw, bh = scale_physical(rect, diam_mm, body_h_mm, PACKAGE_SCALE)

    lead_pitch_scale = bh / diam_mm
    lead_pitch = lead_pitch_mm * lead_pitch_scale
    lead_w = lead_w_mm * lead_pitch_scale

    h_scale = bw / body_h_mm
    lead_len = lead_len_mm * h_scale

    cx = rect.left + rect.width * -0.1
    cy = rect.bottom + rect.height * 0.50

    body_x = cx
    body_y = cy - bh * 0.50

    dome_r = bh * 0.50
    dome_cx = body_x
    dome_cy = cy

    anode_y = cy + lead_pitch * 0.50
    cathode_y = cy - lead_pitch * 0.50

    # -----------------------------------------------------------------
    # Lens style (waterclear vs diffused)
    # -----------------------------------------------------------------
    if lens == "diffused":
        body_rgb = (r, g, b)
        dome_rgb = (r, g, b)
        body_alpha = 0.90
        dome_alpha = 0.90
    else:
        body_rgb = (0.92, 0.92, 0.92)
        dome_rgb = (0.95, 0.95, 0.95)
        body_alpha = 1.00
        dome_alpha = 1.00

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    def fill_rect(x, y, w, h, rgb, a=1.0):
        canvas.setFillColorRGB(*rgb, alpha=a)
        canvas.rect(x, y, w, h, fill=1, stroke=0)

    def fill_path(path, rgb, a=1.0):
        canvas.setFillColorRGB(*rgb, alpha=a)
        canvas.drawPath(path, fill=1, stroke=0)

    # -----------------------------------------------------------------
    # Leads
    # -----------------------------------------------------------------
    fill_rect(body_x + bw, anode_y - lead_w * 0.5, lead_len, lead_w, (0.75, 0.75, 0.75))
    fill_rect(
        body_x + bw,
        cathode_y - lead_w * 0.5,
        lead_len * 0.75,
        lead_w,
        (0.75, 0.75, 0.75),
    )

    # -----------------------------------------------------------------
    # Body
    # -----------------------------------------------------------------
    fill_rect(body_x, body_y, bw, bh, body_rgb, body_alpha)

    # -----------------------------------------------------------------
    # Dome
    # -----------------------------------------------------------------
    arc_x1 = dome_cx - dome_r
    arc_y1 = dome_cy - dome_r
    arc_x2 = dome_cx + dome_r
    arc_y2 = dome_cy + dome_r

    path_dome = canvas.beginPath()
    path_dome.moveTo(dome_cx, dome_cy + dome_r)
    path_dome.arc(arc_x1, arc_y1, arc_x2, arc_y2, 90, 180)
    path_dome.lineTo(dome_cx, dome_cy - dome_r)
    path_dome.close()

    fill_path(path_dome, dome_rgb, dome_alpha)

    # -----------------------------------------------------------------
    # Internal metal: anvil (cathode)
    # -----------------------------------------------------------------
    metal_x_right = body_x + bw
    metal_x_left = body_x + bw * 0.08
    metal_width = metal_x_right - metal_x_left

    anvil_rect_h = lead_w * 2.0
    anvil_tri_h = anvil_rect_h * 0.8
    anvil_rect_y0 = cathode_y - anvil_rect_h * 0.25
    anvil_rect_y1 = anvil_rect_y0 + anvil_rect_h

    fill_rect(
        metal_x_left, anvil_rect_y0, metal_width, anvil_rect_h, (0.45, 0.45, 0.45)
    )

    path_anvil = canvas.beginPath()
    path_anvil.moveTo(metal_x_left, anvil_rect_y1)
    path_anvil.lineTo(metal_x_left, anvil_rect_y1 + anvil_tri_h)
    path_anvil.lineTo(metal_x_right, anvil_rect_y1)
    path_anvil.close()
    fill_path(path_anvil, (0.45, 0.45, 0.45))

    # -----------------------------------------------------------------
    # Internal metal: post (anode)
    # -----------------------------------------------------------------
    post_rect_h = lead_w * 1.2
    post_tri_h = post_rect_h * 0.5
    post_rect_y0 = anode_y - post_rect_h * 0.5

    fill_rect(metal_x_left, post_rect_y0, metal_width, post_rect_h, (0.60, 0.60, 0.60))

    path_post = canvas.beginPath()
    path_post.moveTo(metal_x_right, post_rect_y0)
    path_post.lineTo(metal_x_right, post_rect_y0 - post_tri_h)
    path_post.lineTo(metal_x_left + metal_width * 0.5, post_rect_y0)
    path_post.close()

    fill_path(path_post, (0.60, 0.60, 0.60))

    # -----------------------------------------------------------------
    # Glow effect (waterclear)
    # -----------------------------------------------------------------
    if lens == "waterclear" and wavelength:
        glow_layers = 6
        glow_r = dome_r * 0.8

        for i in range(1, glow_layers + 1):
            f = i / glow_layers
            alpha = 0.50 * (1.0 - f * 0.65)
            radius = glow_r * f
            canvas.setFillColorRGB(r, g, b, alpha=alpha)
            canvas.circle(dome_cx, dome_cy, radius, fill=1, stroke=0)

    # -----------------------------------------------------------------
    # Labels "A" and "K"
    # -----------------------------------------------------------------
    fs = rect.height * 0.25
    canvas.setFont("Helvetica", fs)
    canvas.setFillColor(black)

    label_x = body_x + bw + lead_len * 1.25
    canvas.drawCentredString(label_x, anode_y - fs * 0.25, "A")
    canvas.drawCentredString(label_x, cathode_y - fs * 0.25, "K")
