"""Logging filters, formatters, handlers, and utility functions."""
# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from .config_filter import ConfigFilter
from .context_injection_filter import ContextInjectionFilter
from .queued_handler import QueuedHandler
from . import utils, formatters
from .utils import (
    configure_handler,
    configure_logging,
    get_logger,
    get_queued_logger,
    handle_queued_log_records,
    patch_logging
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
    'configure_handler',
    'configure_logging',
    'get_logger',
    'get_queued_logger',
    'handle_queued_log_records',
    'patch_logging'
]
