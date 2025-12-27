# file: src/core/resistor_value.py

import math


class resistor_value_t:
    """@brief Fixed-point representation of a resistor value."""

    def __init__(self, ohms: float) -> None:
        ohms_exp = 0
        ohms_val = 0

        if ohms != 0.0:
            ohms_exp = math.floor(math.log10(ohms))
            scale = math.pow(10.0, ohms_exp - 2)
            ohms_val = int(round(ohms / scale))

            while ohms_val >= 1000:
                ohms_exp += 1
                ohms_val //= 10

        self.ohms_val = ohms_val
        self.ohms_exp = ohms_exp

    def get_value(self) -> float:
        """@brief Convert back to ohms."""
        scale = math.pow(10.0, float(self.ohms_exp - 2))
        return float(self.ohms_val) * scale

    def _get_prefix(self) -> str:
        if self.ohms_exp >= 12:
            return "T"
        if self.ohms_exp >= 9:
            return "G"
        if self.ohms_exp >= 6:
            return "M"
        if self.ohms_exp >= 3:
            return "k"
        if self.ohms_exp >= 0:
            return ""
        if self.ohms_exp >= -3:
            return "m"
        if self.ohms_exp >= -6:
            return "µ"
        return "n"

    def _get_prefixed_number(self) -> str:
        exp_mod = self.ohms_exp % 3

        if exp_mod == 0:
            if self.ohms_val % 100 == 0:
                return str(self.ohms_val // 100)
            if self.ohms_val % 10 == 0:
                major = self.ohms_val // 100
                minor = (self.ohms_val % 100) // 10
                return f"{major}.{minor}"
            major = self.ohms_val // 100
            minor = self.ohms_val % 100
            return f"{major}.{minor}"

        if exp_mod == 1:
            if self.ohms_val % 10 == 0:
                return str(self.ohms_val // 10)
            major = self.ohms_val // 10
            minor = self.ohms_val % 10
            return f"{major}.{minor}"

        return str(self.ohms_val)

    def format_value(self) -> str:
        """@brief Human-friendly value string with SI prefix."""
        if self.ohms_exp < 0:
            rendered = str(self.ohms_val)
            while rendered.endswith("0"):
                rendered = rendered[:-1]

            if self.ohms_exp == -1:
                return f"0.{rendered}"
            if self.ohms_exp == -2:
                return f"0.0{rendered}"
            if self.ohms_exp == -3:
                return f"0.00{rendered}"

        return f"{self._get_prefixed_number()}{self._get_prefix()}"


# ------------------------------------------------------------
#  Digit codes
# ------------------------------------------------------------


def get_3digit_code(value: resistor_value_t) -> str:
    if value.ohms_val % 10 != 0:
        return ""
    if value.ohms_val == 0:
        return "000"

    digits = str(value.ohms_val // 10)

    if value.ohms_exp > 0:
        multiplier = str(value.ohms_exp - 1)
        return f"{digits}{multiplier}"

    if value.ohms_exp == 0:
        return f"{digits[0]}R{digits[1]}"

    if value.ohms_exp == -1:
        return f"R{digits}"

    if value.ohms_exp == -2:
        if value.ohms_val % 100 != 0:
            return ""
        return f"R0{digits[0]}"

    return ""


def get_4digit_code(value: resistor_value_t) -> str:
    if value.ohms_val == 0:
        return "0000"

    digits = str(value.ohms_val)

    if value.ohms_exp > 1:
        multiplier = str(value.ohms_exp - 2)
        return f"{digits}{multiplier}"

    if value.ohms_exp == 1:
        return f"{digits[0]}{digits[1]}R{digits[2]}"

    if value.ohms_exp == 0:
        return f"{digits[0]}R{digits[1]}{digits[2]}"

    if value.ohms_exp == -1:
        return f"R{digits}"

    if value.ohms_exp == -2:
        if value.ohms_val % 10 != 0:
            return ""
        return f"R0{digits[0]}{digits[1]}"

    if value.ohms_exp == -3:
        if value.ohms_val % 100 != 0:
            return ""
        return f"R00{digits[0]}"

    return ""


def get_eia98_code(value: resistor_value_t) -> str:
    eia = {
        100: "01",
        178: "25",
        316: "49",
        562: "73",
        102: "02",
        182: "26",
        324: "50",
        576: "74",
        105: "03",
        187: "27",
        332: "51",
        590: "75",
        107: "04",
        191: "28",
        340: "52",
        604: "76",
        110: "05",
        196: "29",
        348: "53",
        619: "77",
        113: "06",
        200: "30",
        357: "54",
        634: "78",
        115: "07",
        205: "31",
        365: "55",
        649: "79",
        118: "08",
        210: "32",
        374: "56",
        665: "80",
        121: "09",
        215: "33",
        383: "57",
        681: "81",
        124: "10",
        221: "34",
        392: "58",
        698: "82",
        127: "11",
        226: "35",
        402: "59",
        715: "83",
        130: "12",
        232: "36",
        412: "60",
        732: "84",
        133: "13",
        237: "37",
        422: "61",
        750: "85",
        137: "14",
        243: "38",
        432: "62",
        768: "86",
        140: "15",
        249: "39",
        442: "63",
        787: "87",
        143: "16",
        255: "40",
        453: "64",
        806: "88",
        147: "17",
        261: "41",
        464: "65",
        825: "89",
        150: "18",
        267: "42",
        475: "66",
        845: "90",
        154: "19",
        274: "43",
        487: "67",
        866: "91",
        158: "20",
        280: "44",
        499: "68",
        887: "92",
        162: "21",
        287: "45",
        511: "69",
        909: "93",
        165: "22",
        294: "46",
        523: "70",
        931: "94",
        169: "23",
        301: "47",
        536: "71",
        953: "95",
        174: "24",
        309: "48",
        549: "72",
        976: "96",
    }

    if value.ohms_val not in eia:
        return ""

    digits = eia[value.ohms_val]
    mult = ["Z", "Y", "X", "A", "B", "C", "D", "E", "F"]
    index = value.ohms_exp + 1

    if index < 0 or index >= len(mult):
        return ""

    return f"{digits}{mult[index]}"
