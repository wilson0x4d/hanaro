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
    """A filter to run log messages through python-bidi."""

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal['%', '{', '$'] = '%',
        validate: bool = True,
        *,
        defaults: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Initialize *BidiFormatter* instance."""
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record: logging.LogRecord) -> str:
        """Format the LogRecord, applying bidirectional display behavior."""
        formatted = super().format(record)
        return (
            formatted
            if bidi_fn is None
            else str(bidi_fn(formatted, 'utf-8', False, None, False))
        )


__all__ = [
    'BidiFormatter'
]
