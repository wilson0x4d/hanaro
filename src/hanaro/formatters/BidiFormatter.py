# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from typing import Any, Callable, Literal, Mapping, Optional

bidi_fn:None = None

try: 
    from bidi.algorithm import get_display as bidi_fn # type: ignore
except: # pragma: no cover
    pass

class BidiFormatter(logging.Formatter):
    """
    A filter to run log messages through python-bidi.
    """
    def __init__(
        self,
        fmt:str|None = None,
        datefmt:str|None = None,
        style:Literal['%', '{', '$'] = '%',
        validate:bool = True,
        *,
        defaults:Mapping[str,Any]|None = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record:logging.LogRecord) -> str:
        formatted = super().format(record)
        return formatted if bidi_fn is None else str(bidi_fn(formatted, 'utf-8', False, None, False))

__all__ = [
    'BidiFormatter'
]
