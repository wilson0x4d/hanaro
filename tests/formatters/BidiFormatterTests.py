# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import strings
from hanaro.formatters import BidiFormatter
import logging
from punit import fact
from typing import Any, Callable, Optional

bidi_fn: Optional[Callable[..., Any]] = None

try:
    from bidi.algorithm import get_display as bidi_fn  # type: ignore
except Exception:  # pragma: no cover
    pass


@fact
def basic_verification_test() -> None:
    """Perform basic verification of :class:``BidiFormatter``."""
    fmt = '%(message)s'
    bidi_formatter = BidiFormatter(fmt)
    original = 'test יהוה test'
    record = logging.LogRecord('test', logging.CRITICAL, 'pathname', 123, original, {}, None, None, None)
    expected = str(original if bidi_fn is None else bidi_fn(original))
    actual = bidi_formatter.format(record)
    # NOTE: for human reference only
    print([original, expected, actual])
    assert strings.areSame(expected, actual), f'expected:"{expected}", actual:"{actual}"'
