# file: src/config/config_loader.py

"""
@brief	JSON config loading and validation.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.errors import config_error_t, io_error_t
from src.layout.paper_layouts import get_paper_layouts, paper_config_t
from src.model.devices import (
    active_label_t,
    capacitor_label_t,
    diode_label_t,
    label_t,
    resistor_label_t,
    transistor_label_t,
)
from src.model.specs import diode_spec_t, capacitor_spec_t, transistor_spec_t


@dataclass(frozen=True)
class render_options_t:
    """
    @brief	Render options for a job.
    """

    draw_outlines: bool


@dataclass(frozen=True)
class job_config_t:
    """
    @brief	Resolved job configuration.
    """

    title: str
    layout: paper_config_t
    options: render_options_t
    labels: List[Optional[label_t]]


def load_job_config(path: str) -> job_config_t:
    """
    @brief	Load and validate a job config from JSON.
    @param path	Path to config JSON file.
    @return	Resolved job configuration.
    @warning	Raises io_error_t or config_error_t on failure.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        raise io_error_t("Failed to open config file", detail=str(exc))
    except json.JSONDecodeError as exc:
        raise config_error_t("Invalid JSON in config file", detail=str(exc))

    if not isinstance(data, dict):
        raise config_error_t("Config root must be a JSON object")

    layouts = get_paper_layouts()
    layout_name = str(data.get("layout", "AVERY_L7144"))

    if layout_name not in layouts:
        raise config_error_t(
            "Unknown layout in config file",
            detail=str(layout_name),
        )

    title = str(data.get("title", "Component Labels"))

    options = _parse_options(data.get("options", {}))
    labels = _parse_labels(data.get("labels", []))

    return job_config_t(
        title=title,
        layout=layouts[layout_name],
        options=options,
        labels=labels,
    )


def _parse_options(raw: Dict[str, Any]) -> render_options_t:
    """
    @brief	Parse render options object.
    @param raw	Raw options dict.
    @return	Parsed render options.
    """
    if not isinstance(raw, dict):
        raise config_error_t("options field must be an object")

    return render_options_t(
        draw_outlines=bool(raw.get("draw_outlines", False)),
    )


def _parse_labels(raw: Any) -> List[Optional[label_t]]:
    """
    @brief	Parse label list from config.
    @param raw	Raw labels field.
    @return	List of labels, with None for blanks.
    @warning	Raises config_error_t on schema failure.
    """
    if not isinstance(raw, list):
        raise config_error_t("labels field must be a flat list")

    out: List[Optional[label_t]] = []

    for index, cell in enumerate(raw):
        try:
            if cell is None:
                out.append(None)
            elif isinstance(cell, dict):
                out.append(_parse_label_cell(cell))
            else:
                raise config_error_t(
                    "Each label entry must be an object or null",
                    detail=f"index={index}",
                )
        except config_error_t as exc:
            detail = exc.detail
            if detail is None:
                detail = f"index={index}"
            else:
                detail = f"index={index}, {detail}"
            raise config_error_t(exc.message, detail=detail)

    return out


def _require_field(
    raw: Dict[str, Any],
    field_name: str,
    *,
    context: str,
) -> Any:
    """
    @brief		Fetch a required field or raise a config error.
    @param raw		Input dict.
    @param field_name	Required key.
    @param context	Short context string for error detail.
    @return		Field value.
    @warning		Raises config_error_t if missing.
    """
    if field_name not in raw:
        raise config_error_t(
            "Missing required field",
            detail=f"{context}.{field_name}",
        )
    return raw[field_name]


def _parse_label_cell(raw: Dict[str, Any]) -> label_t:
    """
    @brief	Parse one label object.
    @param raw	Raw label dict.
    @return	Parsed label model.
    @warning	Raises config_error_t on schema failure.
    """
    kind = str(raw.get("kind", "")).lower()
    context = f"label(kind={kind})"

    if kind == "resistor":
        value_ohms_raw = _require_field(raw, "value_ohms", context=context)
        try:
            value_ohms = float(value_ohms_raw)
        except (TypeError, ValueError):
            raise config_error_t(
                "Invalid resistor value_ohms",
                detail=context,
            )

        return resistor_label_t(
            kind="resistor",
            value_ohms=value_ohms,
        )

    if kind == "diode":
        part_number = str(_require_field(raw, "part_number", context=context))
        subtype = str(raw.get("subtype", "diode"))
        package = str(raw.get("package", ""))

        spec_dict = raw.get("spec")
        if spec_dict is None:
            spec = None
        elif not isinstance(spec_dict, dict):
            raise config_error_t("spec for diode must be an object", detail=context)
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
                vwm=spec_dict.get("vwm"),
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
            part_number=part_number,
            subtype=subtype,
            package=package,
            spec=spec,
        )

    if kind == "capacitor":
        part_number = str(_require_field(raw, "part_number", context=context))
        subtype = str(_require_field(raw, "subtype", context=context))
        package = str(raw.get("package", ""))

        spec_raw = raw.get("spec")
        if spec_raw is None:
            spec = None
        elif not isinstance(spec_raw, dict):
            raise config_error_t(
                "spec for capacitor must be an object",
                detail=context,
            )
        else:
            spec = capacitor_spec_t(
                subtype=subtype,
                c=spec_raw.get("c", spec_raw.get("capacitance")),
                v_rated=spec_raw.get("v_rated", spec_raw.get("voltage")),
                tol=spec_raw.get("tol", spec_raw.get("tolerance")),
                dielectric=spec_raw.get("dielectric"),
                t_rated=spec_raw.get("t_rated", spec_raw.get("temperature_range")),
                esr=spec_raw.get("esr"),
                i_ripple=spec_raw.get("i_ripple", spec_raw.get("ripple_current")),
                i_leak=spec_raw.get("i_leak", spec_raw.get("leakage_current")),
                c_min=spec_raw.get("c_min", spec_raw.get("cmin")),
                c_max=spec_raw.get("c_max", spec_raw.get("cmax")),
                f_test=spec_raw.get("f_test", spec_raw.get("vtest")),
            )

        return capacitor_label_t(
            kind="capacitor",
            part_number=part_number,
            subtype=subtype,
            package=package,
            spec=spec,
        )

    if kind == "active":
        part_number = str(_require_field(raw, "part_number", context=context))
        return active_label_t(
            kind="active",
            part_number=part_number,
            role=str(raw.get("role", "")),
            package=str(raw.get("package", "")),
        )

    if kind == "transistor":
        part_number = str(_require_field(raw, "part_number", context=context))
        subtype = str(_require_field(raw, "subtype", context=context))
        package = str(raw.get("package", ""))

        spec_raw = raw.get("spec")
        if spec_raw is None:
            spec = None
        elif not isinstance(spec_raw, dict):
            raise config_error_t(
                "spec for transistor must be an object", detail=context
            )
        else:
            spec = transistor_spec_t(
                pin_config=spec_raw.get("pin_config"),
                i_c_cont=spec_raw.get("i_c_cont"),
                i_c_max=spec_raw.get("i_c_max"),
                p_d=spec_raw.get("p_d"),
                v_ceo=spec_raw.get("v_ceo"),
                h_fe=spec_raw.get("h_fe"),
                f_t=spec_raw.get("f_t"),
                v_be_on=spec_raw.get("v_be_on"),
                v_ds=spec_raw.get("v_ds"),
                i_d_cont=spec_raw.get("i_d_cont"),
                i_d_max=spec_raw.get("i_d_max"),
                r_ds_on=spec_raw.get("r_ds_on"),
                v_gs_th=spec_raw.get("v_gs_th"),
                q_g=spec_raw.get("q_g"),
                i_dss=spec_raw.get("i_dss"),
                v_gs_off=spec_raw.get("v_gs_off"),
                g_m=spec_raw.get("g_m"),
                v_ces=spec_raw.get("v_ces"),
                v_ce_sat=spec_raw.get("v_ce_sat"),
                v_ge_max=spec_raw.get("v_ge_max"),
                e_switch=spec_raw.get("e_switch"),
                q_g_igbt=spec_raw.get("q_g_igbt"),
            )

        return transistor_label_t(
            kind="transistor",
            part_number=part_number,
            subtype=subtype,
            package=package,
            spec=spec,
        )

    raise config_error_t("Unsupported label kind", detail=context)
