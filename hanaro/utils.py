# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import importlib
import os
import appsettings2
import logging
import logging.handlers
import sys

from .ConfigFilter import ConfigFilter
from .ContextInjectionFilter import ContextInjectionFilter
from .QueuedHandler import QueuedHandler


def configureLogging(config:appsettings2.Configuration = None) -> list[logging.Handler]:
    config = config if config is not None else appsettings2.Configuration()
    handlers = []
    defaultLevel = getattr(logging, config.get('logging__level', 'DEBUG').upper())
    defaultFormat = config.get('logging__format', logging.BASIC_FORMAT)
    filters:appsettings2.Configuration = config.get('logging__filters', None)
    configFilter = ConfigFilter(filters.toDictionary() if filters is not None else {})
    contextInjectorFilter = ContextInjectionFilter({}, True)
    datefmt = config.get('logging__datefmt', '%Y-%m-%dT%H:%M:%S')
    # create configured handlers
    handler_configs = config.get('logging__handlers')
    if handler_configs != None:
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
                    if log_path == None:
                        log_path = '.'
                    log_path = os.path.abspath(log_path)
                    os.makedirs(log_path, exist_ok=True)
                    log_name = handler_config.get('name')
                    if log_name == None:
                        log_name = 'adamantium.log'
                    log_name = os.path.join(log_path, log_name)
                    max_size = handler_config.get('max_size')                    
                    if max_size == None:
                        max_size = 4 * 1024 * 1024
                    elif not type(max_size) is int:
                        size_unit = max_size[len(max_size)-3:].upper()
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
                    if max_count == None:
                        max_count = 10
                    else:
                        max_count = int(max_count)
                    handler = logging.handlers.RotatingFileHandler(
                        filename = log_name,
                        encoding = 'utf-8',
                        maxBytes = max_size,
                        backupCount = max_count)
            if handler != None:
                handler.setLevel(getattr(logging, handler_config.get('level', defaultLevel).upper()))
                handler.formatter = logging.Formatter(handler_config.get('format', defaultFormat), datefmt)
                handler.addFilter(configFilter)
                handler.addFilter(contextInjectorFilter)
                handlers.append(handler)
    # log to stdout if no handlers configured
    if len(handlers) == 0:
        handlers.append(logging.StreamHandler(sys.stdout))
    # init
    logging.basicConfig(
        format = defaultFormat,
        datefmt = datefmt,
        handlers = handlers,
        level = defaultLevel,
        force = True
    )
    # return handlers so they can be registered with other loggers if necessary
    logger = logging.getLogger(__name__)
    return handlers

def getLogger(name:str = None, level:int|str = logging.NOTSET) -> logging.Logger:
    """
    Similar to Python's own ``logging.getLogger(...)`` except this function attempts to resolve the name of the calling module when no name has been provided.

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.    
    """
    if name is None:
        import inspect
        name = inspect.currentframe().f_back.f_globals.get('__name__', None)
    logger = logging.getLogger(name)
    if level != logging.NOTSET:
        logger.setLevel(level)
    return logger

def getQueuedLogger(name:str = None, level:int|str = logging.NOTSET) -> logging.Logger:
    """
    Similar to Python's own ``logging.getLogger(...)`` except this function provides a bare-bones Logger that is only configured to forward logging Records to a :py:class:`~hanaro.QueuedHandler` (intentionally bypassing the rest of the logging system.)

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.    
    """
    if name is None:
        import inspect
        name = inspect.currentframe().f_back.f_globals.get('__name__', None)
    logger = logging.Logger(name, level)
    logger.addHandler(QueuedHandler())
    return logger

__all__ = [
    'configureLogging',
    'getLogger',
    'getQueuedLogger'
]
