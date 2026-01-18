# file: src/model/specs.py

"""
@brief 	Specification data models for semiconductor devices.
        Each spec class stores typed electrical parameters and returns
        display-ready strings via a unified .format() method.
"""

from dataclasses import dataclass
from typing import Optional, List

# =====================================================================
# CAPACITOR SPECS
# =====================================================================


@dataclass
class capacitor_spec_t:
    """
    @brief	Unified spec for capacitor devices.
    """

    subtype: str

    c: Optional[str] = None
    v_rated: Optional[str] = None
    tol: Optional[str] = None
    dielectric: Optional[str] = None
    t_rated: Optional[str] = None
    esr: Optional[str] = None
    i_ripple: Optional[str] = None
    i_leak: Optional[str] = None
    c_min: Optional[str] = None
    c_max: Optional[str] = None
    f_test: Optional[str] = None

    def format(self) -> List[str]:
        """
        @brief	Convert populated spec fields into a list of strings
                for the label renderer. Markup-friendly.
        @return	List of display lines.
        """
        lines: List[str] = []
        st = (self.subtype or "").strip().lower()

        if (st in ("variable", "trimmer")) and self.c_min and self.c_max:
            if self.f_test:
                lines.append(f"C = {self.c_min}–{self.c_max} @ {self.f_test}")
            else:
                lines.append(f"C = {self.c_min}–{self.c_max}")
        elif self.c:
            lines.append(f"C = {self.c}")

        if self.v_rated:
            lines.append(f"V_R = {self.v_rated}")

        if self.dielectric and st not in ("ceramic", "monolithic"):
            lines.append(f"dielectric = {self.dielectric}")

        if self.t_rated:
            lines.append(f"T_op = {self.t_rated}")

        if self.esr:
            lines.append(f"ESR = {self.esr}")
        if self.i_ripple:
            lines.append(f"I_ripple = {self.i_ripple}")
        if self.i_leak:
            lines.append(f"I_leak = {self.i_leak}")

        return lines


# =====================================================================
# TRANSISTOR SPECS
# =====================================================================


@dataclass
class transistor_spec_t:
    """
    @brief	Generic spec for BJT, MOSFET, JFET, IGBT.
                Subtype determines which fields are used.
    """

    # Common to all transistor types
    pin_config: Optional[str] = None
    i_c_cont: Optional[str] = None
    i_c_max: Optional[str] = None
    p_d: Optional[str] = None

    # --- BJT ---
    v_ceo: Optional[str] = None
    h_fe: Optional[str] = None
    f_t: Optional[str] = None
    v_be_on: Optional[str] = None

    # --- MOSFET ---
    v_ds: Optional[str] = None
    i_d_cont: Optional[str] = None
    i_d_max: Optional[str] = None
    r_ds_on: Optional[str] = None
    v_gs_th: Optional[str] = None
    q_g: Optional[str] = None

    # --- JFET ---
    i_dss: Optional[str] = None
    v_gs_off: Optional[str] = None
    g_m: Optional[str] = None

    # --- IGBT ---
    v_ces: Optional[str] = None
    v_ce_sat: Optional[str] = None
    v_ge_max: Optional[str] = None
    e_switch: Optional[str] = None
    q_g_igbt: Optional[str] = None

    def format(self) -> List[str]:
        """
        @brief 	Convert populated spec fields into a list of strings
                for the label renderer. Markup-friendly.
        """
        lines: List[str] = []

        # BJT
        if self.v_ceo:
            lines.append(f"V_CEO = {self.v_ceo}")
        if self.i_c_cont:
            lines.append(f"I_C = {self.i_c_cont}")
        if self.i_c_max:
            lines.append(f"I_CM = {self.i_c_max}")
        if self.p_d:
            lines.append(f"P_D = {self.p_d}")
        if self.h_fe:
            lines.append(f"h_FE = {self.h_fe}")
        if self.f_t:
            lines.append(f"f_T = {self.f_t}")
        if self.v_be_on:
            lines.append(f"V_BE(on) = {self.v_be_on}")

        # MOSFET
        if self.v_ds:
            lines.append(f"V_DS = {self.v_ds}")
        if self.i_d_cont:
            lines.append(f"I_D = {self.i_d_cont}")
        if self.i_d_max:
            lines.append(f"I_DM = {self.i_d_max}")
        if self.r_ds_on:
            lines.append(f"R_DS(on) = {self.r_ds_on}")
        if self.v_gs_th:
            lines.append(f"V_GS(th) = {self.v_gs_th}")
        if self.q_g:
            lines.append(f"Q_G = {self.q_g}")

        # JFET
        if self.i_dss:
            lines.append(f"I_DSS = {self.i_dss}")
        if self.v_gs_off:
            lines.append(f"V_GS(off) = {self.v_gs_off}")
        if self.g_m:
            lines.append(f"g_m = {self.g_m}")

        # IGBT
        if self.v_ces:
            lines.append(f"V_CES = {self.v_ces}")
        if self.v_ce_sat:
            lines.append(f"V_CE(sat) = {self.v_ce_sat}")
        if self.v_ge_max:
            lines.append(f"V_GE(max) = {self.v_ge_max}")
        if self.e_switch:
            lines.append(f"E_sw = {self.e_switch}")
        if self.q_g_igbt:
            lines.append(f"Q_G = {self.q_g_igbt}")

        return lines


# =====================================================================
# DIODE SPECS
# =====================================================================


@dataclass
class diode_spec_t:
    """
    @brief	Unified spec class for all diode-based devices.

            Subtype selects schematic symbol and any subtype-specific
            spec display rules.

            All fields are optional. Only non-empty fields appear in output.
    """

    subtype: str  # "diode", "zener", "tvs", "led", "varactor", etc

    # Common diode parameters
    vr: Optional[str] = None
    if_: Optional[str] = None
    vf: Optional[str] = None
    trr: Optional[str] = None
    pin_config: Optional[str] = None

    # Zener
    vz: Optional[str] = None
    izt: Optional[str] = None
    pd: Optional[str] = None
    vbr: Optional[str] = None

    # TVS
    vc: Optional[str] = None
    vwm: Optional[str] = None
    ipk: Optional[str] = None
    ppk: Optional[str] = None

    # LED
    iv: Optional[str] = None
    wavelength: Optional[str] = None
    view_angle: Optional[str] = None
    lens: Optional[str] = None

    # Varactor
    cmin: Optional[str] = None
    cmax: Optional[str] = None
    vtest: Optional[str] = None

    def format(self) -> List[str]:
        """
        @brief	Format spec lines for label output.
        @return	List of display-ready spec lines.
        """
        lines: List[str] = []
        subtype_text = (self.subtype or "").strip().lower()

        def add(label: str, value: Optional[str]) -> None:
            """
            @brief	Append a formatted line if the value is present.
            @param	label	Display label token.
            @param	value	Value string to render.
            """
            if value is None:
                return
            value_text = value.strip()
            if value_text == "":
                return
            lines.append(f"{label} = {value_text}")

        # Common
        add("V_R", self.vr)
        add("I_F", self.if_)
        add("V_F", self.vf)

        # T_rr only where it is meaningful for commutating diodes
        if self.trr is not None and self.trr.strip() != "":
            is_schottky = "schottky" in subtype_text
            is_non_commutating = subtype_text in (
                "zener",
                "tvs",
                "led",
                "varactor",
                "varicap",
            )
            if (not is_schottky) and (not is_non_commutating):
                add("T_rr", self.trr)

        # Zener
        add("V_Z", self.vz)
        add("I_ZT", self.izt)
        add("P_D", self.pd)
        add("V_BR", self.vbr)

        # TVS
        add("V_WM", self.vwm)
        add("V_C", self.vc)
        add("I_pk", self.ipk)
        add("P_pk", self.ppk)

        # LED
        add("I_V", self.iv)
        add("λ", self.wavelength)
        add("θ", self.view_angle)

        # Varactor – special combined format
        if self.cmin and self.cmax:
            if self.vtest:
                lines.append(f"{self.cmin}–{self.cmax} pF @ {self.vtest}")
            else:
                lines.append(f"{self.cmin}–{self.cmax} pF")

        return lines
