# file: src/core/errors.py

"""
@brief Typed exceptions for predictable CLI error handling.
"""


class parts_error_t(Exception):
    """
    @brief	Base exception for PARTS errors.
    """

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(message)


class cli_usage_error_t(parts_error_t):
    """
    @brief	CLI usage or argument errors.
    """


class config_error_t(parts_error_t):
    """
    @brief	Config parse or validation errors.
    """


class io_error_t(parts_error_t):
    """
    @brief	File IO errors.
    """


class render_error_t(parts_error_t):
    """
    @brief	Render or PDF generation errors.
    """
