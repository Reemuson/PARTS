# file: src/core/cli_result.py

"""
@brief CLI result models for success and failure reporting.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class render_result_t:
    """
    @brief	Result summary from a successful render.
    """

    labels_rendered: int
    pages_rendered: int
    output_path: str


@dataclass(frozen=True)
class error_report_t:
    """
    @brief	Normalised error report for consistent CLI output.
    """

    exit_code: int
    message: str
    detail: Optional[str] = None
