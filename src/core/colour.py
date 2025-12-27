# file: src/core/colour.py

from typing import Optional, Tuple


def parse_wavelength(val) -> Optional[float]:
    """@brief Parse wavelength value in nm from mixed inputs."""
    if val is None:
        return None

    if isinstance(val, str) and "/" in val:
        return None

    s = str(val).strip().lower().replace("nm", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def wavelength_to_rgb(val) -> Tuple[float, float, float]:
    """@brief Convert wavelength in nm to approximate RGB tuple."""
    nm = parse_wavelength(val)
    if nm is None:
        return 0.95, 0.95, 1.00

    nm = max(380.0, min(700.0, nm))

    if 380 <= nm < 440:
        r = -(nm - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= nm < 490:
        r = 0.0
        g = (nm - 440) / (490 - 440)
        b = 1.0
    elif 490 <= nm < 510:
        r = 0.0
        g = 1.0
        b = -(nm - 510) / (510 - 490)
    elif 510 <= nm < 580:
        r = (nm - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= nm < 645:
        r = 1.0
        g = -(nm - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0

    if 380 <= nm < 420:
        f = 0.3 + 0.7 * (nm - 380) / (420 - 380)
    elif 645 <= nm < 700:
        f = 0.3 + 0.7 * (700 - nm) / (700 - 645)
    else:
        f = 1.0

    return r * f, g * f, b * f
