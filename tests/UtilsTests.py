# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import logging
from pathlib import Path
from punit import fact, theory, inlinedata

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

@theory
@inlinedata(logging.DEBUG, 'DEBUG', f'because `DEBUG` was specified, expected {__name__}')
@inlinedata(logging.DEBUG, logging.NOTSET, f'because no value was provided, expected {logging.NOTSET}')
def getLogger_levelVerification(expected:str, level:str|int, reason:str) -> None:
    result:logging.Logger = hanaro.getLogger(level=level)
    assert expected == result.level, f'{reason}; actual={result.level}'

@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', f'because `name` was provided, expected "test"')
def getQueuedLogger_levelVerification(expected:str, name:str|None, reason:str) -> None:
    result:logging.Logger = hanaro.getQueuedLogger(name)
    assert expected == result.name, reason


@fact
def configureLogging_acceptsAppsettingsObject() -> None:
    hanaro.configureLogging(appsettings2.getConfiguration())

@fact
def configureLogging_acceptsDictionaryObject() -> None:
    hanaro.configureLogging(appsettings2.getConfiguration().toDictionary())

@fact
def configureLogging_loadsAppsettingsDefault() -> None:
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` is NOT explicitly disabled.
    hanaro.configureLogging()

@fact
def configureLogging_loadsPartialConfigurationObject() -> None:
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` IS explicitly disabled.
    hanaro.configureLogging({
        "logging": {
            "bidi": False
        }
    })


@fact
def configureLogging_loadsAppsettingsCustom() -> None:
    # NOTE: this exists mainly for coverage purposes
    pathlike = Path('tests', 'appsettings')
    hanaro.configureLogging(
        appsettings2.getConfiguration(pathlike)
    )

