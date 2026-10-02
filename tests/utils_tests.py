# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import hanaro
from hanaro import ConfigFilter, ContextInjectionFilter, QueuedHandler
import logging
from punit import fact, theory, inlinedata


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_logger_bvt(expected: str, name: str | None, reason: str) -> None:
    """
    Assert :py:func:``get_logger`` derives correct source name.
    """
    result = hanaro.get_logger(name)
    assert expected == result.name, reason


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_queued_logger_bvt(expected: str, name: str | None, reason: str) -> None:
    """
    Assert :py:func:``get_queued_logger`` derives correct source name.
    """
    result = hanaro.get_queued_logger(name)
    assert expected == result.name, reason


@fact
def get_queued_logger_has_a_queued_handler() -> None:
    """
    Assert :py:func:``get_queued_logger`` has a QueuedHandler assigned to it.
    """
    result = hanaro.get_queued_logger()
    for handler in result.handlers:
        if isinstance(handler, QueuedHandler):
            return
    assert False, 'expected to find a QueuedHandler assigned to the logger.'


@theory
@inlinedata(logging.DEBUG, 'DEBUG', f'because `DEBUG` was specified, expected {__name__}')
@inlinedata(logging.DEBUG, logging.NOTSET, f'because no value was provided, expected {logging.NOTSET}')
def get_logger_has_correct_level(expected: str, level: str | int, reason: str) -> None:
    """
    Assert :py:func:``get_logger`` returns a logger with correct *level* setting.
    """
    result = hanaro.get_logger(level=level)
    assert expected == result.level, f'{reason}; actual={result.level}'


@theory
@inlinedata(__name__, None, f'because `name` was not provided, expected {__name__}')
@inlinedata('test', 'test', 'because `name` was provided, expected "test"')
def get_queued_logger_level_verification(expected: str, name: str | None, reason: str) -> None:
    """
    Assert :py:func:``get_queued_logger`` returns a logger with correct *level* setting.
    """
    result = hanaro.get_queued_logger(name)
    assert expected == result.name, reason


@fact
def configure_logging_accepts_apppsettings2() -> None:
    """
    Assert :py:func:``configure_logging`` accepts an :py:class:``appsettings2.Configuration`` object.
    """
    hanaro.configure_logging(appsettings2.get_configuration())


@fact
def configure_lgging_accepts_dict() -> None:
    """
    Assert :py:func:``configure_logging`` accepts a dictionary.
    """
    hanaro.configure_logging(appsettings2.get_configuration().toDictionary())


@fact
def configure_logging_defaults() -> None:
    """
    Assert :py:func:``configure_logging`` configures defaults.
    """
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` is NOT explicitly disabled.
    hanaro.configure_logging()


@fact
def configure_logging_handles_partial_configuration() -> None:
    """
    Assert :py:func:``configure_logging`` handles a partial logging configuration.
    """
    # NOTE: this configuration gives us code-coverage on default `console` logger when `bidi` IS explicitly disabled.
    hanaro.configure_logging({
        'logging': {
            'bidi': False
        }
    })


@fact
def configure_handler_raises_runtime_error_before_configure_logging() -> None:
    """
    Assert :py:func:``configure_handler`` raises RuntimeError when called before :py:func:``configure_logging``.
    """
    handler = logging.StreamHandler()
    # The module-level globals start as None, so calling configure_handler before
    # configure_logging should raise a RuntimeError.
    # We need to reset the globals to simulate a fresh state.
    import hanaro.utils as utils
    old_config_filter = utils.__config_filter
    old_context_injection_filter = utils.__context_injection_filter
    utils.__config_filter = None
    utils.__context_injection_filter = None
    try:
        try:
            hanaro.configure_handler(handler)
            assert False, 'expected RuntimeError to be raised.'
        except RuntimeError as e:
            assert 'configure_handler() must be called after configure_logging()' in str(e)
    finally:
        utils.__config_filter = old_config_filter
        utils.__context_injection_filter = old_context_injection_filter


@fact
def configure_handler_applies_formatter_and_filters() -> None:
    """
    Assert :py:func:``configure_handler`` applies formatter and filters.
    """
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'file', 'path': '/tmp', 'name': 'test.log'}]}})
    handler = logging.StreamHandler()
    hanaro.configure_handler(handler)
    assert handler.formatter is not None, 'expected formatter to be set by configure_handler'
    assert len(handler.filters) == 2, f'expected 2 filters, got {len(handler.filters)}'
    assert any(isinstance(f, ConfigFilter) for f in handler.filters), 'expected ConfigFilter to be added'
    assert any(isinstance(f, ContextInjectionFilter) for f in handler.filters), 'expected ContextInjectionFilter to be added'


@fact
def configure_handler_preserves_existing_formatter() -> None:
    """
    Assert :py:func:``configure_handler`` does not overwrite an existing formatter.
    """
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'file', 'path': '/tmp', 'name': 'test.log'}]}})
    custom_formatter = logging.Formatter('%(message)s')
    handler = logging.StreamHandler()
    handler.formatter = custom_formatter
    hanaro.configure_handler(handler)
    assert handler.formatter is custom_formatter, 'expected configure_handler to preserve existing formatter'


@fact
def configure_handler_sets_level() -> None:
    """
    Assert :py:func:``configure_handler`` preserves handler level.
    """
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'file', 'path': '/tmp', 'name': 'test.log'}]}})
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    hanaro.configure_handler(handler)
    assert handler.level == logging.WARNING, f'expected handler level to be WARNING, got {handler.level}'


@fact
def configure_handler_does_not_accept_custom_format() -> None:
    """
    Assert :py:func:``configure_handler`` does not accept format/datefmt/level parameters.
    """
    hanaro.configure_logging({'logging': {
        'handlers': [{'type': 'file', 'path': '/tmp', 'name': 'test.log'}],
        'format': '%(message)s',
    }})
    handler = logging.StreamHandler()
    hanaro.configure_handler(handler)
    assert handler.formatter is not None
