# file: src/core/cli_exit_codes.py

"""@brief	CLI exit codes for PARTS."""

from dataclasses import dataclass


@dataclass(frozen=True)
class exit_codes_t:
    """@brief	Exit code definitions."""

    ok: int = 0
    runtime_error: int = 1
    usage_error: int = 2
    config_error: int = 3
    io_error: int = 4
