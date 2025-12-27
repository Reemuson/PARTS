# file: src/layout/label_text.py

from src.packages.api import format_package_for_text as _format_package_for_text


def format_package_for_text(pkg: str) -> str:
    """
    @brief	Format a package string for printing on a label.

    @param pkg	Raw package string from label JSON
    @return	Canonical outline ID if known, else raw input
    """
    return _format_package_for_text(pkg)
