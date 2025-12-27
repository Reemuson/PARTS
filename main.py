# file: main.py
#!/usr/bin/env python3

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from reportlab.pdfgen.canvas import Canvas

from src.core.fonts import load_font_family
from src.config.config_loader import load_job_config
from src.render_engine import render_labels


def _slugify_filename(text: str) -> str:
    """
    @brief	Convert an arbitrary title string into a safe filename stem.
    @param text	Input title.
    @return		Sanitised filename stem.
    """
    s = text.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9._-]", "", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("._-")
    if not s:
        return "component_labels"
    return s


def _parse_output_override(argv: List[str]) -> Optional[str]:
    """
    @brief	Parse optional '--output <file.pdf>' override.
    @param argv	Argv list.
    @return		Output path string, or None if not provided.
    """
    for index, arg in enumerate(argv[2:], start=2):
        if arg == "--output" and (index + 1) < len(argv):
            return str(argv[index + 1])
    return None


def main(argv: List[str]) -> int:
    """
    @brief	Entry point for label generation tool.
    @param argv	Command line arguments.
    @return		Exit status.
    """
    if len(argv) < 2:
        print("Usage: labelgen.py <config.json> [--helvetica] [--output <file.pdf>]")
        return 1

    config_path = str(argv[1])
    font_family = load_font_family(argv)
    job_config = load_job_config(config_path)

    override_output = _parse_output_override(argv)
    if override_output is not None:
        output_path = override_output
    else:
        out_dir = Path("out")
        out_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%y%m%d_%H%M")
        title_stem = _slugify_filename(job_config.title)

        output_path = str(out_dir / f"{timestamp}_{title_stem}.pdf")

    canvas = Canvas(
        output_path,
        pagesize=job_config.layout.pagesize,
    )

    render_labels(
        canvas,
        job_config.layout,
        job_config.labels,
        job_config.options,
        font_family,
    )

    canvas.save()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
