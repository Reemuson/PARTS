# file: src/core/capacitor_value.py

import math
from typing import Optional


class capacitor_value_t:
    """
    @brief	Capacitance value helper for capacitor markings.
    """

    def __init__(self, capacitance_text: str) -> None:
        """
        @brief	                    Parse a capacitance string and store pF as float.
        @param  capacitance_text	Capacitance string (eg "100nF", "4.7uF").
        """
        self.pf_value: float = 0.0
        self.is_valid: bool = False

        pf = _parse_to_pf(capacitance_text)
        if pf is None:
            return

        if pf < 0.0:
            return

        self.pf_value = float(pf)
        self.is_valid = True

    def get_eia_code(self) -> str:
        """
        @brief	Get printed capacitor body code.
        @return	Code string or empty string.
        """
        if not self.is_valid:
            return ""

        pf = self.pf_value

        # < 10 pF -> print literal value (integer or 1 decimal)
        if pf < 10.0:
            if abs(pf - round(pf)) < 0.05:
                return str(int(round(pf)))
            return f"{pf:.1f}".rstrip("0").rstrip(".")

        # >= 10 pF -> 3-digit EIA code
        value = int(round(pf))

        if value < 100:
            return f"{value:02d}0"

        exp = int(math.floor(math.log10(float(value))))
        scale = int(10 ** (exp - 1))
        if scale <= 0:
            return ""

        sig = int(round(value / scale))
        while sig >= 100:
            exp += 1
            scale *= 10
            if scale <= 0:
                return ""
            sig = int(round(value / scale))

        mult = exp - 1
        if 0 <= mult <= 9:
            return f"{sig:02d}{mult}"

        return ""


def tolerance_to_letter(tolerance_text: Optional[str]) -> str:
    """
    @brief	                Map a tolerance string to a common EIA tolerance letter.
    @param  tolerance_text	Tolerance string (eg "+-10%", "±5%").
    @return	                Letter code or empty string if unknown.
    """
    if tolerance_text is None:
        return ""

    key = _normalise_tolerance(tolerance_text)

    table = {
        "+-0.25pf": "C",
        "+-0.5pf": "D",
        "+-1pf": "E",
        "+-1%": "F",
        "+-2%": "G",
        "+-5%": "J",
        "+-10%": "K",
        "+-20%": "M",
        "+80%-20%": "Z",
    }

    return table.get(key, "")


def _normalise_tolerance(text: str) -> str:
    """
    @brief	        Normalise tolerance strings for lookup.
    @param  text	Raw tolerance.
    @return	        Normalised key.
    """
    key = text.strip().lower()
    key = key.replace(" ", "")
    key = key.replace("±", "+-")
    key = key.replace("µ", "u")
    key = key.replace("％", "%")
    key = key.replace("−", "-")
    key = key.replace("--", "-")
    return key


def _parse_to_pf(text: str) -> Optional[float]:
    """
    @brief	        Parse a capacitance string to pF.
    @param  text	Input capacitance string.
    @return	        Value in pF or None if not parseable.
    """
    if not text:
        return None

    s = str(text).strip().lower()
    s = s.replace(" ", "")
    s = s.replace("µ", "u")

    try:
        if s.endswith("pf"):
            return float(s[:-2])
        if s.endswith("nf"):
            return float(s[:-2]) * 1e3
        if s.endswith("uf"):
            return float(s[:-2]) * 1e6
        if s.endswith("mf"):
            return float(s[:-2]) * 1e9
    except ValueError:
        return None

    return None
