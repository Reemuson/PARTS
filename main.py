# file: main.py
#!/usr/bin/env python3

"""
@brief	PARTS label generator CLI entry point.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from reportlab.pdfgen.canvas import Canvas

from src.config.config_loader import load_job_config
from src.core.cli_args import parse_args, print_help_to_stderr, resolve_config_path
from src.core.cli_exit_codes import exit_codes_t
from src.core.cli_output import print_error, print_success
from src.core.cli_result import error_report_t, render_result_t
from src.core.errors import cli_usage_error_t, config_error_t, io_error_t, parts_error_t
from src.core.fonts import load_font_family
from src.render_engine import render_labels


def _slugify_filename(text: str) -> str:
    """
    @brief	Convert an arbitrary title string into a safe filename stem.
    @param text	Input title.
    @return	Sanitised filename stem.
    """
    s = text.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9._-]", "", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("._-")
    if not s:
        return "component_labels"
    return s


def _resolve_output_path(
    job_title: str,
    override_output_path: Optional[str],
) -> str:
    """
    @brief			Resolve output PDF path with an optional override.
    @param job_title		Job title for filename stem.
    @param override_output_path	Explicit output PDF path, if any.
    @return			Output PDF path.
    """
    if override_output_path is not None:
        return str(override_output_path)

    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    title_stem = _slugify_filename(job_title)

    return str(out_dir / f"{timestamp}_{title_stem}.pdf")


def main(argv: List[str]) -> int:
    """
    @brief	Entry point for label generation tool.
    @param argv	Command line arguments.
    @return	Exit status.
    """
    codes = exit_codes_t()

    try:
        args = parse_args(argv)

        try:
            config_path = resolve_config_path(args)
        except cli_usage_error_t as exc:
            print_help_to_stderr(argv)
            print_error(
                error_report_t(
                    exit_code=codes.usage_error,
                    message=exc.message,
                    detail=exc.detail,
                ),
                as_json=bool(args.json),
            )
            return codes.usage_error

        font_family = load_font_family(argv)

        job_config = load_job_config(config_path)
        output_path = _resolve_output_path(job_config.title, args.output_path)

        canvas = Canvas(
            output_path,
            pagesize=job_config.layout.pagesize,
        )

        counts = render_labels(
            canvas,
            job_config.layout,
            job_config.labels,
            job_config.options,
            font_family,
        )

        canvas.save()

        print_success(
            render_result_t(
                labels_rendered=int(counts.labels_rendered),
                pages_rendered=int(counts.pages_rendered),
                output_path=str(output_path),
            ),
            is_quiet=bool(args.quiet),
            as_json=bool(args.json),
        )
        return codes.ok

    except io_error_t as exc:
        print_error(
            error_report_t(
                exit_code=codes.io_error,
                message=exc.message,
                detail=exc.detail,
            ),
            as_json=bool(getattr(args, "json", False)),
        )
        return codes.io_error

    except config_error_t as exc:
        print_error(
            error_report_t(
                exit_code=codes.config_error,
                message=exc.message,
                detail=exc.detail,
            ),
            as_json=bool(getattr(args, "json", False)),
        )
        return codes.config_error

    except parts_error_t as exc:
        print_error(
            error_report_t(
                exit_code=codes.runtime_error,
                message=exc.message,
                detail=exc.detail,
            ),
            as_json=bool(getattr(args, "json", False)),
        )
        return codes.runtime_error

    except Exception as exc:
        print_error(
            error_report_t(
                exit_code=codes.runtime_error,
                message="Unhandled error",
                detail=str(exc),
            ),
            as_json=bool(getattr(args, "json", False)),
        )
        return codes.runtime_error


if __name__ == "__main__":
    sys.exit(main(sys.argv))
