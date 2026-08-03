# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Provides helper methods such as ``configure_logging``, ``get_logger(...)``, etc."""

from __future__ import annotations

import appsettings2
import contextvars
from datetime import datetime, timezone
import importlib
import logging
import logging.handlers
import os
import sys
import threading
from typing import Any, Callable, Optional, cast

from .formatters.BidiFormatter import BidiFormatter
from .ConfigFilter import ConfigFilter
from .ContextInjectionFilter import ContextInjectionFilter
from .QueuedHandler import QueuedHandler


_CIF_contextvar: contextvars.ContextVar[Optional[ContextInjectionFilter]] = (
    contextvars.ContextVar('_CIF_contextvar', default=None)
)
__original_get_logger: Optional[Callable[[Optional[str]], logging.Logger]] = None
__allow_queued_logger: bool = True


def configure_logging(
    configuration: Optional[dict[str, Any] | appsettings2.Configuration] = None,
    force: bool = False
) -> list[logging.Handler]:
    """
    Configure logging according to the *configuration* provided.

    :param configuration: The configuration object to pull logging settings from. Omit to apply defaults.
    :param force: Should configuration be applied (forced) even if handlers have already been configured?
    :return: A list of handlers which are configured.
    """
    if configuration is not None:
        if isinstance(configuration, dict):
            configuration = appsettings2.Configuration.fromDictionary(configuration)
    else:
        configuration = appsettings2.Configuration()
    if force or not logging.getLogger().hasHandlers():
        global __allow_queued_logger
        __allow_queued_logger = configuration.get('logging__allow_queued_logger', True)
        handlers = list[logging.Handler]()
        default_bidi_enabled = cast(bool, configuration.get('logging__bidi', True))
        default_level = cast(str, configuration.get('logging__level', 'DEBUG')).upper()
        default_format = configuration.get('logging__format', logging.BASIC_FORMAT)
        filter_configs = configuration.get('logging__filters', None)
        config_filter = ConfigFilter("config_filter", filter_configs.toDictionary() if filter_configs is not None else {})
        context_injection_filter = ContextInjectionFilter({}, True)
        datefmt = configuration.get('logging__datefmt', '%Y-%m-%dT%H:%M:%S')
        # create configured handlers
        handler_configs = configuration.get('logging__handlers')
        if handler_configs is not None:
            for handler_config in handler_configs:
                handler = None
                match str(handler_config.get('type')).lower():
                    case 'custom':
                        module_name, class_name = handler_config.get('class').rsplit('.', 1)
                        module = importlib.import_module(module_name)
                        handler_class = getattr(module, class_name)
                        args = handler_config.get('args')
                        handler = handler_class(**(args.toDictionary() if args is not None else {}))
                    case 'console':
                        handler = logging.StreamHandler(sys.stdout)
                    case 'file':
                        log_path = handler_config.get('path')
                        if log_path is None:
                            log_path = 'logs'
                        log_path = os.path.abspath(log_path)
                        os.makedirs(log_path, exist_ok=True)
                        log_name = handler_config.get('name')
                        if log_name is None:
                            log_name = f"{cast(str, handler_config.get('level', 'log'))}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log".lower()
                        log_name = os.path.join(log_path, log_name)
                        max_size: str | int | None = handler_config.get('max_size')
                        max_size = max_size if max_size is not None else 4 * 1024 * 1024
                        if type(max_size) is str:
                            size_unit = max_size[len(max_size) - 3:].upper()
                            match size_unit:
                                case 'KIB':
                                    max_size = int(max_size[:-3]) * 1024
                                case 'MIB':
                                    max_size = int(max_size[:-3]) * 1024 * 1024
                                case 'GIB':
                                    max_size = int(max_size[:-3]) * 1024 * 1024 * 1024
                                case _:
                                    max_size = int(max_size)
                        max_count = handler_config.get('max_count')
                        if max_count is None:
                            max_count = 10
                        else:
                            max_count = int(max_count)
                        handler = logging.handlers.RotatingFileHandler(
                            filename=log_name,
                            encoding='utf-8',
                            maxBytes=cast(int, max_size),
                            backupCount=max_count)
                if handler is not None:
                    handler.setLevel(getattr(logging, handler_config.get('level', default_level).upper()))
                    if handler.formatter is None:
                        if (
                            default_bidi_enabled
                            and isinstance(handler, logging.StreamHandler)
                            and handler.stream is sys.stdout
                        ):
                            handler.formatter = BidiFormatter(handler_config.get('format', default_format), datefmt)
                        else:
                            handler.formatter = logging.Formatter(handler_config.get('format', default_format), datefmt)
                    handler.addFilter(config_filter)
                    handler.addFilter(context_injection_filter)
                    handlers.append(handler)
        # log to stdout if no handlers configured
        if len(handlers) == 0:
            handler = logging.StreamHandler(sys.stdout)
            if default_bidi_enabled:
                handler.formatter = BidiFormatter(default_format, datefmt)
            else:
                handler.formatter = logging.Formatter(default_format, datefmt)
            handlers.append(handler)
        # init
        logging.basicConfig(
            format=default_format,
            datefmt=datefmt,
            handlers=handlers,
            level=default_level,
            force=True
        )
        _ = logging.getLogger(__name__)
        return handlers
    else:
        logger = logging.getLogger(__name__)
        logger.warning('Handlers were already configured and `force != True`.')
        return []


def get_logger(name: Optional[str] = None, level: int | str = logging.NOTSET, allow_queued_logger: bool | None = None) -> logging.Logger:
    """
    Similar to Python's own ``logging.getLogger(...)`` except this function attempts to resolve the name of the calling module when no name has been provided.

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance.
    """
    if allow_queued_logger is None:
        allow_queued_logger = __allow_queued_logger
    if name is None:
        try:
            import inspect
            f = inspect.currentframe()
            name = (
                None
                if f is None or f.f_back is None
                else (
                    f.f_globals.get('__name__', None)
                    if f.f_back is None
                    else f.f_back.f_globals.get('__name__', None)
                )
            )
        except Exception:
            pass  # NOP
    logger: logging.Logger
    if allow_queued_logger is not False and threading.current_thread() is not threading.main_thread():
        logger = get_queued_logger(name)
    elif __original_get_logger is not None:
        logger = __original_get_logger(name)
    else:
        logger = logging.getLogger(name)
    ctx = _CIF_contextvar.get()
    if ctx is not None:
        logger.addFilter(ctx)
    if level != logging.NOTSET:
        logger.setLevel(level)
    return logger


def __get_queued_logger(name: Optional[str] = None, level: int | str = logging.NOTSET) -> logging.Logger:
    if __allow_queued_logger is not True:
        if __original_get_logger is not None:
            logger = __original_get_logger(name)
        else:
            logger = logging.getLogger(name)
    elif name is None:
        try:
            import inspect
            f = inspect.currentframe()
            name = (
                None if f is None or f.f_back is None else
                f.f_back.f_globals.get('__name__', None) if f.f_back.f_back is None else
                f.f_back.f_back.f_globals.get('__name__', None)
            )
        except Exception:
            pass  # NOP
    logger = logging.Logger(cast(str, name), level)
    logger.addHandler(QueuedHandler())
    return logger


def get_queued_logger(name: Optional[str] = None, level: int | str = logging.NOTSET) -> logging.Logger:
    """
    Similar to Python's own ``logging.getLogger(...)`` except this function provides a bare-bones Logger that is only configured to forward logging Records to a :py:class:`~hanaro.QueuedHandler` (intentionally bypassing the rest of the logging system).

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.
    """
    return __get_queued_logger(name, level)


def handle_queued_log_records() -> None:
    """
    Output all queued log records using the root logger.

    This is a QOL function for devs using `get_queued_logger`.

    ```python
    while not exitProgram:
        doProgramLogic()
        hanaro.handle_queued_log_records()
        # (consider signal or sleep to play nice with CPU)
    ```

    This function must be called on the main thread. Calling from any other thread will have undefined behavior and is not supported.
    """
    while (log_record := QueuedHandler.get_log_record()) is not None:
        logging.root.callHandlers(log_record)


def patch_logging() -> None:
    """
    Patch ``hanaro.get_logger`` into ``logging.getLogger``, so that code unaware of hanaro can indirectly use it without requiring a code change.
    """
    global __original_get_logger
    if __original_get_logger is None:
        __original_get_logger = logging.getLogger
        logging.getLogger = get_logger


############################
#       deprecations       #
############################


configureLogging = configure_logging  # noqa: N816
"""⚠️ DEPRECATED: use ``configure_logging(...)`` instead."""


getLogger = get_logger  # noqa: N816
"""⚠️ DEPRECATED: use ``get_logger(...)`` instead."""


getQueuedLogger = get_queued_logger  # noqa: N816
"""⚠️ DEPRECATED: use ``get_queued_logger(...)`` instead."""


handleQueuedLogRecords = handle_queued_log_records  # noqa: N816
"""⚠️ DEPRECATED: use ``handle_queued_log_records(...)`` instead."""


__all__ = [
    'configure_logging',
    'get_logger',
    'get_queued_logger',
    'handle_queued_log_records',
    'patch_logging',
    # deprecated exports (since 1.0.0)
    'configureLogging',
    'getLogger',
    'getQueuedLogger',
    'handleQueuedLogRecords',
]
