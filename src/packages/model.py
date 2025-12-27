# file: src/packages/model.py

"""
@brief	Package resolution models for the PARTS system.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class resolved_package_t:
    """
    @brief		Resolved package record used by the package draw pipeline.

    @param raw_key	Raw key provided by label JSON
    @param canonical_id	Canonical outline id (eg "TO-220-AB")
    @param print_id	Canonical id to print (variant if present)
    @param family_id	Renderer family id, None if not renderable yet
    @param params	Merged mechanical parameters for the family
    @param qualifiers	Non-print qualifiers (eg ["epoxy", "fullpack"])
    @param is_renderableTrue if a family is assigned and registered
    """

    raw_key: str
    canonical_id: str
    print_id: str
    family_id: Optional[str]
    params: Dict[str, Any]
    qualifiers: List[str]
    is_renderable: bool
