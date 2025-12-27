# file: src/config/config_loader.py

import json
from dataclasses import dataclass
from typing import Optional, Any, Dict, List

from src.layout.paper_layouts import paper_config_t, get_paper_layouts
from src.model.devices import (
    label_t,
    resistor_label_t,
    diode_label_t,
    capacitor_label_t,
    active_label_t,
    transistor_label_t,
)

from src.model.specs import diode_spec_t, transistor_spec_t


# ======================================================================
# RENDER OPTIONS
# ======================================================================


@dataclass
class render_options_t:
    draw_both_sides: bool
    draw_center_line: bool
    draw_outlines: bool


@dataclass
class job_config_t:
    title: str
    layout: paper_config_t
    options: render_options_t
    labels: List[Optional[label_t]]


# ======================================================================
# MAIN LOADER
# ======================================================================


def load_job_config(path: str) -> job_config_t:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    layouts = get_paper_layouts()
    layout_name = str(data.get("layout", "AVERY_L7144"))

    if layout_name not in layouts:
        raise ValueError(f"Unknown layout '{layout_name}' in config file.")

    title = str(data.get("title", "Component Labels"))

    options = _parse_options(data.get("options", {}))
    labels = _parse_labels(data.get("labels", []))

    return job_config_t(
        title=title,
        layout=layouts[layout_name],
        options=options,
        labels=labels,
    )


# ======================================================================
# OPTION PARSER
# ======================================================================


def _parse_options(raw: Dict[str, Any]) -> render_options_t:
    return render_options_t(
        draw_both_sides=bool(raw.get("draw_both_sides", False)),
        draw_center_line=bool(raw.get("draw_center_line", False)),
        draw_outlines=bool(raw.get("draw_outlines", False)),
    )


# ======================================================================
# LABEL LIST PARSER
# ======================================================================


def _parse_labels(raw: Any) -> List[Optional[label_t]]:
    if not isinstance(raw, list):
        raise ValueError("labels field must be a flat list.")

    out: List[Optional[label_t]] = []

    for cell in raw:
        if cell is None:
            out.append(None)
        elif isinstance(cell, dict):
            out.append(_parse_label_cell(cell))
        else:
            raise ValueError("Each label entry must be an object or null.")

    return out


# ======================================================================
# INDIVIDUAL LABEL PARSER
# ======================================================================


def _parse_label_cell(raw: Dict[str, Any]) -> label_t:
    kind = str(raw.get("kind", "")).lower()

    # RESISTOR
    if kind == "resistor":
        return resistor_label_t(
            kind="resistor",
            value_ohms=float(raw["value_ohms"]),
        )

    # DIODE
    if kind == "diode":
        pn = str(raw["part_number"])
        subtype = str(raw.get("subtype", "diode"))
        package = str(raw.get("package", ""))

        spec_dict = raw.get("spec")
        if spec_dict is None:
            spec = None
        elif not isinstance(spec_dict, dict):
            raise ValueError("spec for diode must be an object")
        else:
            spec = diode_spec_t(
                subtype=subtype,
                vr=spec_dict.get("vr"),
                if_=spec_dict.get("if"),
                vf=spec_dict.get("vf"),
                trr=spec_dict.get("trr"),
                vz=spec_dict.get("vz"),
                izt=spec_dict.get("izt"),
                pd=spec_dict.get("pd"),
                vbr=spec_dict.get("vbr"),
                vc=spec_dict.get("vc"),
                ipk=spec_dict.get("ipk"),
                ppk=spec_dict.get("ppk"),
                iv=spec_dict.get("iv"),
                wavelength=spec_dict.get("wavelength"),
                view_angle=spec_dict.get("view"),
                lens=spec_dict.get("lens"),
                cmin=spec_dict.get("cmin"),
                cmax=spec_dict.get("cmax"),
                vtest=spec_dict.get("vtest"),
                pin_config=spec_dict.get("pin_config"),
            )

        return diode_label_t(
            kind="diode",
            part_number=pn,
            subtype=subtype,
            package=package,
            spec=spec,
        )

    # CAPACITOR
    if kind == "capacitor":
        return capacitor_label_t(
            kind="capacitor",
            value=str(raw["value"]),
            voltage=str(raw.get("voltage", "")),
            dielectric=str(raw.get("dielectric", "")),
        )

    # ACTIVE (tbd)
    if kind == "active":
        return active_label_t(
            kind="active",
            part_number=str(raw["part_number"]),
            role=str(raw.get("role", "")),
            package=str(raw.get("package", "")),
        )

    # TRANSISTOR (BJT, MOSFET, JFET, IGBT)
    if kind == "transistor":
        pn = str(raw["part_number"])
        subtype = str(raw["subtype"])
        package = str(raw.get("package", ""))

        spec_raw = raw.get("spec")
        if spec_raw is None:
            spec = None
        elif not isinstance(spec_raw, dict):
            raise ValueError("spec for transistor must be a dict")
        else:
            spec = transistor_spec_t(
                # Common
                pin_config=spec_raw.get("pin_config"),
                i_c_cont=spec_raw.get("i_c_cont"),
                i_c_max=spec_raw.get("i_c_max"),
                p_d=spec_raw.get("p_d"),
                # BJT
                v_ceo=spec_raw.get("v_ceo"),
                h_fe=spec_raw.get("h_fe"),
                f_t=spec_raw.get("f_t"),
                v_be_on=spec_raw.get("v_be_on"),
                # MOSFET
                v_ds=spec_raw.get("v_ds"),
                i_d_cont=spec_raw.get("i_d_cont"),
                i_d_max=spec_raw.get("i_d_max"),
                r_ds_on=spec_raw.get("r_ds_on"),
                v_gs_th=spec_raw.get("v_gs_th"),
                q_g=spec_raw.get("q_g"),
                # JFET
                i_dss=spec_raw.get("i_dss"),
                v_gs_off=spec_raw.get("v_gs_off"),
                g_m=spec_raw.get("g_m"),
                # IGBT
                v_ces=spec_raw.get("v_ces"),
                v_ce_sat=spec_raw.get("v_ce_sat"),
                v_ge_max=spec_raw.get("v_ge_max"),
                e_switch=spec_raw.get("e_switch"),
                q_g_igbt=spec_raw.get("q_g_igbt"),
            )

        return transistor_label_t(
            kind="transistor",
            part_number=pn,
            subtype=subtype,
            package=package,
            spec=spec,
        )

    raise ValueError(f"Unsupported label kind '{kind}'.")
