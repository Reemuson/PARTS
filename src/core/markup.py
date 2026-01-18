# file: src/core/markup.py
# lightweight markup text renderer for ReportLab
# Supports:
#   - Subscripts: I_pk, V_br, h_fe
#   - Superscripts: 10^-3, m^2
#   - Greek names: lambda, mu, omega, phi...
#   - Plus-minus shorthand: +-
#   - En dash shorthand: --

GREEK_MAP = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "theta": "θ",
    "lambda": "λ",
    "mu": "µ",
    "omega": "ω",
    "sigma": "σ",
    "phi": "φ",
    "psi": "ψ",
}


def measure_markup(
    canvas, text: str, font: str = "Helvetica", size: float = 10.0
) -> float:
    """
    Measure marked-up text width in points without drawing.
    """
    cx = 0.0
    i = 0
    n = len(text)

    while i < n:
        # -------------------------------
        # Plus-minus shorthand
        # -------------------------------
        if text[i : i + 2] == "+-":
            canvas.setFont(font, size)
            cx += canvas.stringWidth("±", font, size)
            i += 2
            continue
        # -------------------------------
        # En dash shorthand
        # -------------------------------
        if text[i : i + 2] == "--":
            canvas.setFont(font, size)
            cx += canvas.stringWidth("–", font, size)
            i += 2
            continue

        ch = text[i]

        # -------------------------------
        # Greek symbols
        # -------------------------------
        if ch.isalpha():
            matched = False
            for name, symbol in GREEK_MAP.items():
                ln = len(name)
                if text[i : i + ln].lower() == name:
                    canvas.setFont(font, size)
                    cx += canvas.stringWidth(symbol, font, size)
                    i += ln
                    matched = True
                    break

            if matched:
                continue

            canvas.setFont(font, size)
            cx += canvas.stringWidth(ch, font, size)
            i += 1
            continue

        # -------------------------------
        # Subscript
        # -------------------------------
        if ch == "_" and i + 1 < n:
            i += 1
            sub = []
            while i < n and text[i].isalnum():
                sub.append(text[i])
                i += 1
            sub = "".join(sub)

            sub_size = size * 0.70
            canvas.setFont(font, sub_size)
            cx += canvas.stringWidth(sub, font, sub_size)
            continue

        # -------------------------------
        # Superscript
        # -------------------------------
        if ch == "^" and i + 1 < n:
            i += 1
            sup = []
            while i < n and text[i].isalnum():
                sup.append(text[i])
                i += 1
            sup = "".join(sup)

            sup_size = size * 0.70
            canvas.setFont(font, sup_size)
            cx += canvas.stringWidth(sup, font, sup_size)
            continue

        # -------------------------------
        # Default character
        # -------------------------------
        canvas.setFont(font, size)
        cx += canvas.stringWidth(ch, font, size)
        i += 1

    return cx


def draw_markup(
    canvas,
    x: float,
    y: float,
    text: str,
    font: str = "Helvetica",
    size: float = 10.0,
) -> float:
    """
    Draw marked-up text onto a ReportLab canvas.
    Returns final x position after drawing.
    """
    cx = x
    i = 0
    n = len(text)

    while i < n:
        # -------------------------------
        # Plus-minus shorthand
        # -------------------------------
        if text[i : i + 2] == "+-":
            canvas.setFont(font, size)
            canvas.drawString(cx, y, "±")
            cx += canvas.stringWidth("±", font, size)
            i += 2
            continue

        # -------------------------------
        # En dash shorthand
        # -------------------------------
        if text[i : i + 2] == "--":
            canvas.setFont(font, size)
            canvas.drawString(cx, y, "–")
            cx += canvas.stringWidth("–", font, size)
            i += 2
            continue

        ch = text[i]

        # -------------------------------
        # Greek symbols
        # -------------------------------
        if ch.isalpha():
            matched = False
            for name, symbol in GREEK_MAP.items():
                ln = len(name)
                if text[i : i + ln].lower() == name:
                    canvas.setFont(font, size)
                    canvas.drawString(cx, y, symbol)
                    cx += canvas.stringWidth(symbol, font, size)
                    i += ln
                    matched = True
                    break

            if matched:
                continue

            canvas.setFont(font, size)
            canvas.drawString(cx, y, ch)
            cx += canvas.stringWidth(ch, font, size)
            i += 1
            continue

        # -------------------------------
        # Subscript
        # -------------------------------
        if ch == "_" and i + 1 < n:
            i += 1
            sub = []
            while i < n and text[i].isalnum():
                sub.append(text[i])
                i += 1
            sub = "".join(sub)

            sub_size = size * 0.70
            canvas.setFont(font, sub_size)
            canvas.drawString(cx, y - sub_size * 0.35, sub)
            cx += canvas.stringWidth(sub, font, sub_size)
            continue

        # -------------------------------
        # Superscript
        # -------------------------------
        if ch == "^" and i + 1 < n:
            i += 1
            sup = []
            while i < n and text[i].isalnum():
                sup.append(text[i])
                i += 1
            sup = "".join(sup)

            sup_size = size * 0.70
            canvas.setFont(font, sup_size)
            canvas.drawString(cx, y + sup_size * 0.60, sup)
            cx += canvas.stringWidth(sup, font, sup_size)
            continue

        # -------------------------------
        # Default character
        # -------------------------------
        canvas.setFont(font, size)
        canvas.drawString(cx, y, ch)
        cx += canvas.stringWidth(ch, font, size)
        i += 1

    return cx
