# file: src/packages/axial_resistor.py

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import gray, HexColor, toColor


def _resistor_color_table(num: int) -> HexColor:
    table = [
        HexColor("#000000"),
        HexColor("#964B00"),
        HexColor("#FF3030"),
        HexColor("#FFA500"),
        HexColor("#FFFF00"),
        HexColor("#00FF00"),
        HexColor("#0000FF"),
        HexColor("#C520F6"),
        HexColor("#808080"),
        HexColor("#FFFFFF"),
    ]
    return table[num]


def _draw_fancy_stripe(
    canvas: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    colours,
) -> None:
    canvas.setFillColor(colours[2])
    canvas.rect(x, y + height * 5 / 6, width, height / 6, fill=1, stroke=0)
    canvas.setFillColor(colours[1])
    canvas.rect(x, y + height * 4 / 6, width, height / 6, fill=1, stroke=0)
    canvas.setFillColor(colours[0])
    canvas.rect(x, y + height * 3 / 6, width, height / 6, fill=1, stroke=0)
    canvas.setFillColor(colours[1])
    canvas.rect(x, y + height * 2 / 6, width, height / 6, fill=1, stroke=0)
    canvas.setFillColor(colours[2])
    canvas.rect(x, y + height * 1 / 6, width, height / 6, fill=1, stroke=0)
    canvas.setFillColor(colours[3])
    canvas.rect(x, y, width, height / 6, fill=1, stroke=0)


def _draw_stripe_border(canvas, x, y, width, height):
    canvas.setLineWidth(0.3)
    canvas.setFillColor(gray, 0.0)
    canvas.setStrokeColorRGB(0.2, 0.2, 0.2, 0.5)
    canvas.rect(x, y, width, height, fill=0, stroke=1)


def draw_resistor_stripe(
    canvas: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    value: int,
) -> None:

    if 0 <= value <= 9:
        canvas.setFillColor(_resistor_color_table(value))
        canvas.rect(x, y, width, height, fill=1, stroke=0)
        _draw_stripe_border(canvas, x, y, width, height)
        return

    if value == -1:  # gold
        gold = [
            HexColor("#FFF0A0"),
            HexColor("#FFE55C"),
            HexColor("#FFD700"),
            HexColor("#D1B000"),
        ]
        _draw_fancy_stripe(canvas, x, y, width, height, gold)
        _draw_stripe_border(canvas, x, y, width, height)
        return

    if value == -2:  # silver
        silver = [
            HexColor("#D0D0D0"),
            HexColor("#A9A9A9"),
            HexColor("#929292"),
            HexColor("#7B7B7B"),
        ]
        _draw_fancy_stripe(canvas, x, y, width, height, silver)
        _draw_stripe_border(canvas, x, y, width, height)
        return

    # unknown stripe
    canvas.setLineWidth(0.5)
    canvas.setFillColor(gray, 0.3)
    canvas.setStrokeColorRGB(0.5, 0.5, 0.5, 1.0)
    canvas.rect(x, y, width, height, fill=1, stroke=1)
    canvas.line(x, y, x + width, y + height)
    canvas.line(x + width, y, x, y + height)


def draw_resistor_body(
    canvas: Canvas,
    value,
    colour1,
    colour2,
    x: float,
    y: float,
    width: float,
    height: float,
    num_codes: int,
) -> None:
    """@brief Draw resistor body + stripes."""

    if value.ohms_exp < num_codes - 4:
        return

    border = height / 6.0
    body_height = height - 2 * border
    corner = body_height / 4.0

    # gradient body
    canvas.saveState()
    path = canvas.beginPath()
    path.roundRect(
        x + border,
        y + border,
        width - 2 * border,
        body_height,
        corner,
    )
    canvas.clipPath(path, stroke=0)
    canvas.linearGradient(
        x + width / 2.0,
        y + border + height,
        x + width / 2.0,
        y + border,
        (colour1, colour2),
    )
    canvas.restoreState()

    width_nc = width - 2 * border - 2 * corner
    stripe_w = width_nc / 10.0
    stripe_h = body_height

    # stripes
    if value.ohms_val == 0:
        draw_resistor_stripe(
            canvas,
            x + border + corner + stripe_w / 2 + 2 * stripe_w * 2,
            y + border,
            stripe_w,
            stripe_h,
            0,
        )
    else:
        for index in range(num_codes):
            if index == num_codes - 1:
                stripe_value = value.ohms_exp + 2 - num_codes
            else:
                stripe_value = value.ohms_val
                for _ in range(2 - index):
                    stripe_value //= 10
                stripe_value %= 10

            draw_resistor_stripe(
                canvas,
                x + border + corner + stripe_w / 2 + 2 * stripe_w * float(index),
                y + border,
                stripe_w,
                stripe_h,
                stripe_value,
            )

        # tolerance stripe
        draw_resistor_stripe(
            canvas,
            x + width - border - corner - stripe_w * 1.5,
            y + border,
            stripe_w,
            stripe_h,
            -3,
        )

    # outline
    canvas.setFillColor("black")
    canvas.setStrokeColor("black")
    canvas.setLineWidth(0.5)
    canvas.roundRect(
        x + border,
        y + border,
        width - 2 * border,
        body_height,
        corner,
    )
