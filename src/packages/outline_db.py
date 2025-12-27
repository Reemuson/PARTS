# file: src/packages/outline_db.py

"""
@brief	Canonical outline database and alias registry.

        This file is the source of truth for which outlines exist and how
        aliases and variants resolve to canonical ids.
"""

from typing import Any, Dict, List, Optional, Tuple


outline_t = dict[str, Any]

OUTLINES: Dict[str, outline_t] = {}
PACKAGE_ALIASES: Dict[str, str] = {}
PACKAGE_VARIANTS: Dict[str, dict[str, Any]] = {}


def _normalise_alias_key(raw: str) -> str:
    """
    @brief	Normalise an alias lookup key.

    @param raw	Input key
    @return	Normalised key suitable for lookups
    """
    if not raw:
        return ""
    key = raw.strip().upper()
    key = key.replace(" ", "")
    key = key.replace("_", "")
    return key


def _register_outline(
    canonical_id: str,
    *,
    domain: str,
    group: str,
    family_id: Optional[str] = None,
    params: Optional[dict[str, Any]] = None,
    aliases: Optional[List[str]] = None,
) -> None:
    """
    @brief		Register an outline, optionally renderable.

    @param canonical_id	Canonical outline id
    @param domain		"DO", "TO" or another taxonomy domain
    @param group		Grouping label
    @param family_id	Renderer family id
    @param params		Mechanical params for the family
    @param aliases		Optional alias strings
    """
    entry: outline_t = {
        "id": canonical_id,
        "domain": domain,
        "group": group,
    }
    if family_id is not None:
        entry["family_id"] = family_id
    if params is not None:
        entry["params"] = dict(params)

    OUTLINES[canonical_id] = entry

    if aliases:
        for alias in aliases:
            _register_alias(alias, canonical_id)


def _register_alias(alias: str, canonical_id: str) -> None:
    """
    @brief		Register a pure alias mapping to an outline.

    @param alias		Alias string
    @param canonical_id	Canonical outline id
    """
    key = _normalise_alias_key(alias)
    if key:
        PACKAGE_ALIASES[key] = canonical_id


def _register_variant(
    variant_id: str,
    base_id: str,
    overrides: dict[str, Any],
    *,
    aliases: Optional[List[str]] = None,
) -> None:
    """
    @brief		Register a variant of an outline.

                    The variant is printed as variant_id, but it inherits family and
                    base params from base_id, with overrides applied.

    @param variant_id	Canonical variant id (printed id)
    @param base_id		Canonical base outline id
    @param overrides	Mechanical override params
    @param aliases		Optional alias strings mapping to this variant
    """
    record = {
        "base_id": base_id,
        "variant_id": variant_id,
        "overrides": dict(overrides),
    }

    key = _normalise_alias_key(variant_id)
    if key:
        PACKAGE_VARIANTS[key] = dict(record)

    if aliases:
        for alias in aliases:
            alias_key = _normalise_alias_key(alias)
            if alias_key:
                PACKAGE_VARIANTS[alias_key] = dict(record)


def _seed_full_outline_registry() -> None:
    """
    @brief	Seed OUTLINES with known canonical list.

            This registers every outline as known, but not necessarily renderable.
            Renderable outlines are then overridden with family and params.
    """
    do_groups: List[Tuple[str, List[str]]] = [
        ("Button Rectifier", ["DO-217"]),
        ("Disc Type", ["DO-200"]),
        ("Flanged Mount Family", ["DO-211"]),
        ("Leadless Family", ["DO-213"]),
        ("Lead Mounted Family", ["DO-204"]),
        (
            "Plastic Surface-Mount Family",
            [
                "DO-214",
                "DO-215",
                "DO-216",
                "DO-218",
                "DO-219",
                "DO-220",
                "DO-221",
                "DO-222",
            ],
        ),
        (
            "Round Body Axial Lead",
            [
                "DO-201-AA",
                "DO-202-AA",
                "DO-204-AA",
                "DO-204-AC",
                "DO-204-AF",
                "DO-204-AG",
                "DO-204-AH",
                "DO-204-AL",
            ],
        ),
        ("Round Body Axial Type", ["DO-201"]),
        ("Single-End Press-Fit", ["DO-208", "DO-209"]),
        ("Stud-Hex Base", ["DO-203", "DO-205"]),
        ("Terminal Stud Axial Lead", ["DO-203-AB"]),
    ]

    for group, ids in do_groups:
        for outline_id in ids:
            _register_outline(outline_id, domain="DO", group=group)

    to_groups: List[Tuple[str, List[str]]] = [
        (
            "Axial Leads",
            [
                "TO-9",
                "TO-42",
                "TO-72",
                "TO-73",
                "TO-74",
                "TO-75",
                "TO-76",
                "TO-77",
                "TO-78",
                "TO-79",
                "TO-80",
                "TO-96",
                "TO-97",
                "TO-99",
                "TO-100",
                "TO-101",
                "TO-205-AA",
                "TO-205-AB",
                "TO-206-AA",
                "TO-205-AC",
                "TO-205-AD",
                "TO-206-AB",
                "TO-233-AA",
            ],
        ),
        ("Ceramic No Lead", ["TO-276"]),
        ("Coaxial Type", ["TO-215"]),
        ("Disc Type Family", ["TO-200"]),
        (
            "Diamond Base",
            [
                "TO-37",
                "TO-66",
                "TO-204-AA",
                "TO-204-AB",
                "TO-213-AB",
                "TO-213-AC",
            ],
        ),
        (
            "Double-Ended Flatpack",
            [
                "TO-87",
                "TO-88",
                "TO-89",
                "TO-90",
                "TO-91",
                "TO-95",
            ],
        ),
        ("Dual-in-Package", ["TO-250"]),
        (
            "Flange-Mounted Header Family",
            [
                "TO-204",
                "TO-213",
                "TO-218",
                "TO-219",
                "TO-220",
                "TO-238",
                "TO-257",
                "TO-258",
                "TO-259",
                "TO-262",
                "TO-264",
                "TO-267",
                "TO-280",
                "TO-281",
            ],
        ),
        ("Flange-Mounted Package", ["TO-273"]),
        ("Flange-Mounted Peripheral Terminal", ["TO-247", "TO-254"]),
        ("Flange-Mounted Rectangular Base", ["TO-244"]),
        ("Flat Index Axial Leaded", ["TO-92"]),
        ("Flat Leads", ["TO-225-AA", "TO-232-AA"]),
        ("Flat Mounted Transistor", ["TO-256", "TO-282"]),
        ("Flexible Terminals", ["TO-209"]),
        (
            "Header Family",
            [
                "TO-205",
                "TO-206",
                "TO-236",
                "TO-237",
                "TO-243",
                "TO-251",
                "TO-252",
                "TO-260",
                "TO-263",
                "TO-268",
                "TO-279",
            ],
        ),
        ("Multiple-Ended Flatpack", ["TO-84", "TO-85", "TO-86"]),
        ("Opto Family Insertion Mount", ["TO-266"]),
        ("Plastic Clip Mounted Package", ["TO-274"]),
        ("Power Package", ["TO-265", "TO-270", "TO-272", "TO-275"]),
        ("Quad Flack Pack Surface Mount", ["TO-271"]),
        ("Small Outline", ["TO-269"]),
        ("Small Outline Transistor (SOT)", ["TO-253", "TO-261"]),
        ("Solid Terminals", ["TO-208"]),
        ("Stud-Mount Flex Lead", ["TO-94"]),
        ("Stud-Mounted Stripline", ["TO-216"]),
        ("Tab-Mounted Peripheral Leads", ["TO-202"]),
        ("Terminal Strip Power Module", ["TO-240"]),
    ]

    for group, ids in to_groups:
        for outline_id in ids:
            _register_outline(outline_id, domain="TO", group=group)

    gen_groups: List[Tuple[str, List[str]]] = [
        ("Axial Diode", ["R-6"]),
        ("Axial Diode", ["T-18"]),
    ]

    for group, ids in gen_groups:
        for i in ids:
            _register_outline(i, domain="GEN", group=group)


def _seed_current_renderables() -> None:
    """
    @brief	Seed renderable outline mappings to existing families.
    """
    axial_family = "axial_round_body"

    _register_outline(
        "DO-201-AA",
        domain="DO",
        group="Round Body Axial Lead",
        family_id=axial_family,
        params={"len": 8.35, "dia": 5.3, "material": "epoxy"},
        aliases=["DO-27"],
    )

    _register_outline(
        "DO-204-AH",
        domain="DO",
        group="Round Body Axial Lead",
        family_id=axial_family,
        params={"len": 3.9, "dia": 1.7, "material": "glass"},
        aliases=["DO-35"],
    )
    _register_outline(
        "DO-204-AL",
        domain="DO",
        group="Round Body Axial Lead",
        family_id=axial_family,
        params={"len": 4.7, "dia": 2.7, "material": "epoxy"},
        aliases=["DO-41"],
    )
    _register_outline(
        "DO-204-AC",
        domain="DO",
        group="Round Body Axial Lead",
        family_id=axial_family,
        params={"len": 7.0, "dia": 3.6, "material": "epoxy"},
        aliases=["DO-15"],
    )
    _register_outline(
        "DO-204-AF",
        domain="DO",
        group="Round Body Axial Lead",
        family_id=axial_family,
        params={"len": 9.5, "dia": 5.3, "material": "epoxy"},
        aliases=["DO-29"],
    )
    _register_outline(
        "DO-201-AD",
        domain="DO",
        group="Round Body Axial Type",
        family_id=axial_family,
        params={"len": 9.0, "dia": 5.1, "material": "epoxy"},
        aliases=["DO-201"],
    )

    _register_outline(
        "TO-92",
        domain="TO",
        group="Flat Index Axial Leaded",
        family_id="to92_moulded",
        params={
            "pin_count": 3,
            "body_w": 4.8,
            "body_h": 4.8,
            "lead_len": 11.0,
            "lead_pitch": 1.27,
        },
        aliases=["TO92"],
    )

    _register_outline(
        "TO-204-AA",
        domain="TO",
        group="Diamond Base",
        family_id="to204_diamond",
        params={
            "pin_count": 2,
            "pin_arc_start_deg": 65.0,
            "pin_arc_stop_deg": -65.0,
            "pin_diameter_mm": 1.0,
            "is_body_pin": True,
        },
        aliases=["TO-3", "TO3"],
    )

    _register_outline(
        "TO-205-AD",
        domain="TO",
        group="Axial Leads",
        family_id="to205_package",
        params={
            "pin_count": 3,
            "pin_diameter_mm": 1.0,
            "pin_connected_to_body": 3,
        },
        aliases=["TO-205", "TO205", "TO-39", "TO39"],
    )

    _register_outline(
        "TO-206-AA",
        domain="TO",
        group="Axial Leads",
        family_id="to206_package",
        params={
            "pin_count": 3,
            "pin_diameter_mm": 1.0,
            "pin_connected_to_body": 3,
        },
        aliases=["TO-206", "TO206", "TO-18", "TO18"],
    )

    _register_outline(
        "TO-218-AA",
        domain="TO",
        group="Flat Leads",
        family_id="to218_tab",
        params={"pin_count": 3, "tab_is_pin": True},
        aliases=["TO-218"],
    )
    _register_variant(
        "TO-218-5",
        "TO-218-AA",
        {"pin_count": 5, "tab_is_pin": True},
    )

    _register_outline(
        "TO-225-AA",
        domain="TO",
        group="Flat Leads",
        family_id="to225_tab",
        params={"pin_count": 3, "tab_is_pin": True},
        aliases=["TO-126", "TO126"],
    )

    _register_outline(
        "TO-220-AB",
        domain="TO",
        group="Flange-Mounted Header Family",
        family_id="to220_tab",
        params={"pin_count": 3, "tab_is_pin": True, "tab_finish": "metallic"},
        aliases=["TO-220", "TO220"],
    )
    _register_variant(
        "TO-220-AA",
        "TO-220-AB",
        {"pin_count": 3, "tab_is_pin": False, "tab_finish": "metallic"},
    )
    _register_variant(
        "TO-220-AC",
        "TO-220-AB",
        {"pin_count": 2, "tab_is_pin": True, "tab_finish": "metallic"},
    )
    _register_variant(
        "TO-220-AB-5L",
        "TO-220-AB",
        {"pin_count": 5},
        aliases=["TO-220-5", "TO220-5", "TO-220-5L"],
    )
    _register_variant(
        "TO-220-AB-6L",
        "TO-220-AB",
        {"pin_count": 6},
        aliases=["TO-220-6", "TO220-6", "TO-220-6L"],
    )
    _register_variant(
        "TO-220-AB-7L",
        "TO-220-AB",
        {"pin_count": 7},
        aliases=["TO-220-7", "TO220-7", "TO-220-7L"],
    )
    _register_variant(
        "TO-220-F",
        "TO-220-AB",
        {"pin_count": 3, "tab_is_pin": True, "tab_finish": "insulated"},
        aliases=["TO220F", "TO-220F"],
    )

    _register_outline(
        "TO-243-AA",
        domain="TO",
        group="Header Family",
        family_id="to243_tab",
        params={
            "body_w": 4.5,
            "body_h": 2.76,
        },
        aliases=["TO243", "SOT-89", "SOT89"],
    )
    _register_variant(
        "TO-243-AB",
        "TO-243-AA",
        {"pin_count": 3},
        aliases=["TO243AB", "SOT-89-2", "SOT89-2"],
    )
    _register_variant(
        "TO-243-6",
        "TO-243-AA",
        {"pin_count": 6},
        aliases=["TO243-6", "SOT-89-6", "SOT89-6"],
    )

    _register_outline(
        "TO-247",
        domain="TO",
        group="Flange-Mounted Peripheral Terminal",
        family_id="to247_tab",
        params={
            "pin_count": 3,
            "body_w": 20.0,
            "body_h": 15.6,
            "lead_len": 20.0,
        },
        aliases=["TO247"],
    )
    _register_variant(
        "TO-247-4",
        "TO-247",
        {"pin_count": 4},
    )

    _register_outline(
        "TO-264",
        domain="TO",
        group="Flange-Mounted Header Family",
        family_id="to264_body",
        params={
            "body_mm": 20.0,
            "height_mm": 26.0,
            "lead_mm": 20.0,
            "hole_d_mm": 3.81,
            "scallop_d_mm": 6.35,
            "scallop_y_mm": 6.0,
            "pin_count": 3,
            "pin_pitch_mm": 5.75,
        },
        aliases=["TO264", "TO-264AA", "TO-3P"],
    )

    _register_variant(
        "TO-264-2",
        "TO-264",
        {"pin_count": 2},
        aliases=["TO264-2", "TO-264-2L"],
    )

    _register_variant(
        "TO-264-5",
        "TO-264",
        {"pin_count": 5, "pin_pitch_mm": 3.81},
        aliases=["TO264-5", "TO-264-5L"],
    )

    _register_outline(
        "DO-213-AB",
        domain="DO",
        group="Leadless Family",
        family_id="melf",
        params={
            "body_length": 5,
            "body_diameter": 2.4,
            "pad_width": 0.55,
            "material": "glass",
        },
        aliases=["MELF", "MMB", "SOD-106"],
    )

    for outline_id, params, aliases in [
        (
            "DO-214-AC",
            {"body_w": 4.3, "body_h": 2.6, "pad_w": 1.2, "pad_h": 1.45},
            ["SMA"],
        ),
        (
            "DO-214-AA",
            {"body_w": 4.32, "body_h": 3.62, "pad_w": 1.2, "pad_h": 2.1},
            ["SMB"],
        ),
        (
            "DO-214-AB",
            {"body_w": 6.86, "body_h": 5.9, "pad_w": 1.2, "pad_h": 2.97},
            ["SMC"],
        ),
    ]:
        _register_outline(
            outline_id,
            domain="DO",
            group="Plastic Surface-Mount Family",
            family_id="smd_2pad",
            params=params,
            aliases=aliases,
        )

    _register_outline(
        "SOT-23",
        domain="TO",
        group="Small Outline Transistor (SOT)",
        family_id="smd_3lead",
        params={
            "body_w": 2.9,
            "body_h": 1.3,
            "pad2_w": 0.4,
            "pad2_h": 0.6,
            "pad2_pitch": 1.9,
            "pad1_w": 0.4,
            "pad1_h": 0.6,
            "pin_count": 3,
        },
        aliases=[
            "SOT23",
            "SOT-23-3",
            "SOT23-3",
            "TO-236",
            "TO-236AA",
            "SOT-23F",
        ],
    )

    _register_variant(
        "SOT-23-4",
        "SOT-23",
        {
            "pin_count": 4,
        },
        aliases=["SOT23-4", "SOT-23-4L", "SOT23-4L"],
    )

    _register_variant(
        "SOT-23-5",
        "SOT-23",
        {
            "pin_count": 5,
        },
        aliases=["SOT23-5", "SOT-23-5L", "SOT23-5L"],
    )

    _register_variant(
        "SOT-23-6",
        "SOT-23",
        {
            "pin_count": 6,
        },
        aliases=["SOT23-6", "SOT-23-6L", "SOT23-6L"],
    )

    _register_variant(
        "SOT-23-8",
        "SOT-23",
        {
            "pin_count": 8,
        },
        aliases=["SOT23-8", "SOT-23-8L", "SOT23-8L"],
    )

    _register_outline(
        "SOT-323",
        domain="EIAJ",
        group="Small Outline Transistor (SOT)",
        family_id="smd_3lead",
        params={
            "body_w": 2.2,
            "body_h": 1.35,
            "pad2_w": 0.4,
            "pad2_h": 0.425,
            "pad2_pitch": 1.3,
            "pad1_w": 0.4,
            "pad1_h": 0.525,
            "pin_count": 3,
        },
        aliases=[
            "SOT323",
            "SOT-323-3",
            "SOT323-3",
            "SC-70",
        ],
    )

    _register_outline(
        "R-6",
        domain="GEN",
        group="Axial Diode",
        family_id="axial_round_body",
        params={
            "len": 8.8,
            "dia": 8.8,
            "material": "epoxy",
        },
        aliases=["R6"],
    )

    _register_outline(
        "T-18",
        domain="GEN",
        group="Axial Diode",
        family_id="axial_round_body",
        params={
            "len": 8.8,
            "dia": 3.5,
            "material": "epoxy",
        },
        aliases=["T18"],
    )

    _register_outline(
        "5MM ROUND T/H",
        domain="IEC",
        group="Leaded LED",
        family_id="led_tht_round",
        params={
            "body_d": 5.0,
            "body_h": 8.6,
            "lead_len": 17.0,
            "lead_pitch": 2.54,
            "lead_w": 0.6,
        },
        aliases=["LED5MM", "5MMLED"],
    )


_seed_full_outline_registry()
_seed_current_renderables()
