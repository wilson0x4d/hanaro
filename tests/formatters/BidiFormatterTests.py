# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import strings
from hanaro.formatters import BidiFormatter
import logging
from punit import fact
from typing import Callable, Optional

bidi_fn:None = None

try: 
    from bidi.algorithm import get_display as bidi_fn # type: ignore
except: # pragma: no cover
    pass

@fact
def bidiFormatter_bvt() -> None:
    fmt = f'%(message)s'
    nonbidi_formatter = logging.Formatter(fmt)
    bidi_formatter = BidiFormatter(fmt)
    original = 'test יהוה test'
    record = logging.LogRecord('test', logging.CRITICAL, 'pathname', 123, original, {}, None, None, None)
    expected = str(original if bidi_fn is None else bidi_fn(original))
    actual = bidi_formatter.format(record)
    # NOTE: for human reference only
    print([original, expected, actual])
    assert strings.areSame(expected, actual), f'expected:"{expected}", actual:"{actual}"'
