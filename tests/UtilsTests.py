# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import hanaro
import logging
from pathlib import Path
from punit import fact, theory, inlinedata


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_logger_bvt(expected: str, name: str | None, reason: str) -> None:
    """Assert :function:``get_logger`` derives correct source name."""
    result = hanaro.get_logger(name)
    assert expected == result.name, reason


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_queued_logger_bvt(expected: str, name: str | None, reason: str) -> None:
    """Assert :function:``get_queued_logger`` derives correct source name."""
    result = hanaro.get_queued_logger(name)
    assert expected == result.name, reason


@fact
def get_queued_logger_has_a_queued_handler() -> None:
    """Assert :function:``get_queued_logger`` has a QueuedHandler assigned to it."""
    result = hanaro.get_queued_logger()
    for handler in result.handlers:
        if isinstance(handler, hanaro.QueuedHandler):
            return
    assert False, 'expected to find a QueuedHandler assigned to the logger.'


@theory
@inlinedata(logging.DEBUG, 'DEBUG', f'because `DEBUG` was specified, expected {__name__}')
@inlinedata(logging.DEBUG, logging.NOTSET, f'because no value was provided, expected {logging.NOTSET}')
def get_logger_has_correct_level(expected: str, level: str | int, reason: str) -> None:
    """Assert :function:``get_logger`` returns a logger with correct *level* setting."""
    result = hanaro.get_logger(level=level)
    assert expected == result.level, f'{reason}; actual={result.level}'


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_queued_logger_level_verification(expected: str, name: str | None, reason: str) -> None:
    """Assert :function:``get_queued_logger`` returns a logger with correct *level* setting."""
    result = hanaro.get_queued_logger(name)
    assert expected == result.name, reason


@fact
def configure_logging_accepts_apppsettings2() -> None:
    """Assert :function:``configure_logging`` accepts an :class:``appsettings2.Configuration`` object."""
    hanaro.configure_logging(appsettings2.get_configuration())


@fact
def configure_lgging_accepts_dict() -> None:
    """Assert :function:``configure_logging`` accepts a dictionary."""
    hanaro.configure_logging(appsettings2.get_configuration().toDictionary())


@fact
def configure_logging_defaults() -> None:
    """Assert :function:``configure_logging`` configures defaults ."""
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` is NOT explicitly disabled.
    hanaro.configure_logging()


@fact
def configure_logging_handles_partial_configuration() -> None:
    """Assert :function:``configure_logging`` handles a partial logging configuration."""
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` IS explicitly disabled.
    hanaro.configure_logging({
        "logging": {
            "bidi": False
        }
    })
