# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from punit import *

import hanaro

@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', f'because `name` was provided, expected "test"')
def getLogger_nameVerification(expected:str, name:str|None, reason:str) -> None:
    result:logging.Logger = hanaro.getLogger(name)
    assert expected == result.name, reason

@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', f'because `name` was provided, expected "test"')
def getQueuedLogger_nameVerification(expected:str, name:str|None, reason:str) -> None:
    result:logging.Logger = hanaro.getQueuedLogger(name)
    assert expected == result.name, reason

@fact
def getQueuedLogger_mustHaveQueuedHandler() -> None:
    result:logging.Logger = hanaro.getQueuedLogger()
    wasFound:bool = False
    for handler in result.handlers:
        if isinstance(handler, hanaro.QueuedHandler):
            wasFound = True
            break
    assert wasFound
