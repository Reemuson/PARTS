# file: src/packages/resolve.py

"""
@brief	Package resolver for canonical ids, variants and qualifiers.
"""

from typing import Any, Dict, List, Optional, Tuple

from src.packages.outline_db import OUTLINES, PACKAGE_ALIASES, PACKAGE_VARIANTS
from src.packages.model import resolved_package_t


def _normalise_lookup(raw: str) -> str:
    """
    @brief	Normalise a package string for alias and variant lookups.

    @param raw	Raw key from label JSON.
    @return	Normalised key.
    """
    if not raw:
        return ""
    key = raw.strip().upper()
    key = key.replace(" ", "")
    key = key.replace("_", "")
    return key


def _split_qualifiers(raw: str) -> Tuple[str, List[str]]:
    """
    @brief	Split raw package key and non-print qualifiers.

    Qualifiers use '@', eg "DO-204-AL@glass".

    @Note: Qualifiers are preserved (lowercased) and returned as a list,
    but only the base key participates in outline lookup. This means
    "DISC@5@blue" will resolve base "DISC" and qualifiers ["5","blue"].

    @param raw	Raw key.
    @return	(base_key, qualifiers)
    """
    if not raw:
        return "", []
    parts = raw.split("@")
    base = parts[0].strip()
    qualifiers: List[str] = []
    for q in parts[1:]:
        qt = q.strip().lower()
        if qt:
            qualifiers.append(qt)
    return base, qualifiers


def _apply_qualifiers(
    params: Dict[str, Any],
    qualifiers: List[str],
) -> None:
    """
    @brief		Apply qualifiers to params without affecting print id.

    @param params	Params to mutate.
    @param qualifiers	Qualifier tokens.
    @return		None.
    """
    for q in qualifiers:
        if q in ["glass", "epoxy", "blue", "metallic", "yellow"]:
            params["material"] = q
        elif q in ["fullpack", "insulated", "f"]:
            params["tab_finish"] = "insulated"
        else:
            existing = params.get("qualifiers")
            if isinstance(existing, list):
                existing.append(q)
            elif existing is None:
                params["qualifiers"] = [q]


def _resolve_to_ids_and_overrides(
    raw_key: str,
) -> Tuple[str, str, Dict[str, Any]]:
    """
    @brief		Resolve key to canonical id, print id and overrides.

    @param raw_key	Raw key, qualifiers already stripped.
    @return		(canonical_id, print_id, overrides)
    """
    key = _normalise_lookup(raw_key)
    overrides: Dict[str, Any] = {}

    variant = PACKAGE_VARIANTS.get(key)
    if variant is not None:
        base_id = str(variant.get("base_id", ""))
        variant_id = str(variant.get("variant_id", ""))
        ov = variant.get("overrides", {})
        if isinstance(ov, dict):
            overrides = dict(ov)
        return base_id, variant_id if variant_id else base_id, overrides

    alias = PACKAGE_ALIASES.get(key)
    if alias is not None:
        return alias, alias, overrides

    if key in OUTLINES:
        return key, key, overrides

    return "", "", overrides


def resolve_package(raw_package: str) -> Optional[resolved_package_t]:
    """
    @brief		Resolve a package string to a renderable package description.

    @param raw_package	Raw key from label JSON.
    @return		Resolved package or None if unknown.
    """
    base_key, qualifiers = _split_qualifiers(raw_package)
    canonical_id, print_id, overrides = _resolve_to_ids_and_overrides(base_key)
    if not canonical_id:
        return None

    entry = OUTLINES.get(canonical_id)
    if not isinstance(entry, dict):
        return None

    family_id = entry.get("family_id")
    base_params = entry.get("params", {})

    params: Dict[str, Any] = {}
    if isinstance(base_params, dict):
        params.update(base_params)
    params.update(overrides)
    _apply_qualifiers(params, qualifiers)

    is_renderable = bool(isinstance(family_id, str) and family_id)

    return resolved_package_t(
        raw_key=raw_package,
        canonical_id=canonical_id,
        print_id=print_id,
        family_id=family_id if isinstance(family_id, str) else None,
        params=params,
        qualifiers=qualifiers,
        is_renderable=is_renderable,
    )
