# file: src/core/cli_output.py

"""
@brief Output formatting for human and JSON CLI modes.
"""

import json
import sys
from dataclasses import asdict

from src.core.cli_result import error_report_t, render_result_t


def print_success(
    result: render_result_t,
    *,
    is_quiet: bool,
    as_json: bool,
) -> None:
    """
    @brief		Print success to stdout.
    @param result	Success result.
    @param is_quiet	Whether to suppress non-error output.
    @param as_json	Whether to emit JSON.
    @return		None.
    """
    if is_quiet:
        return

    if as_json:
        payload = {"ok": True, "result": asdict(result)}
        print(json.dumps(payload, ensure_ascii=False), file=sys.stdout)
        return

    msg = (
        f"OK: wrote PDF -> {result.output_path} "
        f"(labels={result.labels_rendered}, pages={result.pages_rendered})"
    )
    print(msg, file=sys.stdout)


def print_error(report: error_report_t, *, as_json: bool) -> None:
    """
    @brief		Print error to stderr.
    @param report	Error report.
    @param as_json	Whether to emit JSON.
    @return		None.
    """
    if as_json:
        payload = {"ok": False, "error": asdict(report)}
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return

    if report.detail is None:
        print(f"ERROR[{report.exit_code}]: {report.message}", file=sys.stderr)
        return

    print(
        f"ERROR[{report.exit_code}]: {report.message} ({report.detail})",
        file=sys.stderr,
    )
