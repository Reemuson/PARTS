# file: src/model/devices.py

"""
@brief Device label type definitions for the PARTS system.
"""

from dataclasses import dataclass
from typing import Optional, Union, Literal, List

from src.model.specs import diode_spec_t, capacitor_spec_t, transistor_spec_t


device_kind_t = Literal[
    "resistor",
    "diode",
    "capacitor",
    "active",
    "transistor",
]


# =====================================================================
# RESISTOR
# =====================================================================


@dataclass
class resistor_label_t:
    kind: Literal["resistor"]
    value_ohms: float


# =====================================================================
# DIODE
# =====================================================================


@dataclass
class diode_label_t:
    kind: Literal["diode"]
    part_number: str
    subtype: str = "diode"
    package: str = ""
    spec: Optional[diode_spec_t] = None


# =====================================================================
# CAPACITOR
# =====================================================================


@dataclass
class capacitor_label_t:
    kind: Literal["capacitor"]
    part_number: str
    subtype: str
    package: str = ""
    spec: Optional[capacitor_spec_t] = None


# =====================================================================
# TRANSISTOR
# =====================================================================


@dataclass
class transistor_label_t:
    kind: Literal["transistor"]
    part_number: str
    subtype: str
    package: str = ""
    spec: Optional[transistor_spec_t] = None


# =====================================================================
# ACTIVE
# =====================================================================


@dataclass
class active_label_t:
    kind: Literal["active"]
    part_number: str
    role: str = ""
    package: str = ""


# =====================================================================
# LABEL LIST TYPES
# =====================================================================

label_t = Union[
    resistor_label_t,
    diode_label_t,
    capacitor_label_t,
    active_label_t,
    transistor_label_t,
]

label_grid_t = List[List[Optional[label_t]]]
label_flat_t = List[Optional[label_t]]
