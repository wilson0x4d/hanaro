"""Logging filters, formatters, handlers, and utility functions."""
# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigFilter import ConfigFilter
from .ContextInjectionFilter import ContextInjectionFilter
from .QueuedHandler import QueuedHandler
from . import utils, formatters
from .utils import (
    configure_logging,
    get_logger,
    get_queued_logger,
    handle_queued_log_records,
    # deprecated exports (since 1.0.0)
    configureLogging,
    getLogger,
    getQueuedLogger,
    handleQueuedLogRecords
)


__version__ = '0.0.0'
__commit__ = '0abc123'
__all__ = [
    '__version__', '__commit__',
    'ConfigFilter',
    'ContextInjectionFilter',
    'formatters',
    'QueuedHandler',
    'utils',
    'configure_logging',
    'get_logger',
    'get_queued_logger',
    'handle_queued_log_records',
    # deprecated exports (since 1.0.0)
    'configureLogging',
    'getLogger',
    'getQueuedLogger',
    'handleQueuedLogRecords'
]
