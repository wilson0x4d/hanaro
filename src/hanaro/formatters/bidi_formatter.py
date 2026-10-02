# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from typing import Any, Callable, Literal, Mapping, Optional

bidi_fn: Optional[Callable[..., Any]] = None

try:
    from bidi.algorithm import get_display as bidi_fn  # type: ignore
except Exception:  # pragma: no cover
    pass


class BidiFormatter(logging.Formatter):
    """
    A log formatter that applies bidirectional text display to log messages.

    This formatter runs log messages through python-bidi to properly display
    text containing bidirectional characters (such as Arabic or Hebrew text).
    If python-bidi is not installed, messages are returned unmodified.

    Usage
    -----

    .. code-block:: python

        formatter = BidiFormatter('%(message)s')
        handler.setFormatter(formatter)
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal['%', '{', '$'] = '%',
        validate: bool = True,
        *,
        defaults: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Initialize a *BidiFormatter* instance.

        :param fmt: The format string to use, defaults to ``None``.
        :param datefmt: The date format string to use, defaults to ``None``.
        :param style: The style of the format string ('%', '{', or '$').
        :param validate: Whether to validate the format string.
        :param defaults: A dictionary of default values for format string keys.
        """
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the LogRecord, applying bidirectional display behavior.

        :param record: The LogRecord to format.
        :returns: The formatted string with bidirectional text applied.
        """
        formatted = super().format(record)
        return (
            formatted
            if bidi_fn is None
            else str(bidi_fn(formatted, 'utf-8', False, None, False))
        )


__all__ = [
    'BidiFormatter'
]
