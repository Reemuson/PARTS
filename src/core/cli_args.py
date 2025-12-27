# file: src/core/cli_args.py

"""
@brief CLI argument parsing and resolution helpers.
"""

import argparse
import sys

from src.core.errors import cli_usage_error_t


def build_argument_parser() -> argparse.ArgumentParser:
    """
    @brief	Build the argument parser.
    @return	Configured parser.
    """
    epilog_lines = [
        "Examples:",
        "  python main.py ./src/config/leds_config.json",
        "  python main.py --config ./src/config/leds_config.json",
        "  python main.py ./cfg.json --output ./out/labels.pdf",
        "  python main.py ./cfg.json --json",
    ]
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Generate PARTS component labels as a PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(epilog_lines),
    )

    parser.add_argument("config", nargs="?", help="Path to job config JSON.")
    parser.add_argument(
        "--config",
        dest="config_override",
        help="Path to job config JSON (overrides positional).",
    )

    parser.add_argument(
        "--output",
        dest="output_path",
        help="Output PDF path. Default: ./out/<timestamp>_<title>.pdf",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable extra diagnostic output.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON status.",
    )

    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    @brief	Parse CLI args.
    @param argv	Full argv list including program name.
    @return	Parsed args.
    """
    parser = build_argument_parser()
    return parser.parse_args(argv[1:])


def resolve_config_path(args: argparse.Namespace) -> str:
    """
    @brief	Resolve config path from args.
    @param args	Parsed args.
    @return	Config path string.
    @warning	Raises cli_usage_error_t if missing.
    """
    if args.config_override is not None:
        return str(args.config_override)
    if args.config is not None:
        return str(args.config)

    raise cli_usage_error_t(
        "Missing config path",
        detail="Provide <config.json> or --config <config.json>",
    )


def print_help_to_stderr(argv: list[str]) -> None:
    """
    @brief	Print help text to stderr.
    @param argv	Full argv list including program name.
    @return	None.
    """
    parser = build_argument_parser()
    parser.print_help(sys.stderr)
