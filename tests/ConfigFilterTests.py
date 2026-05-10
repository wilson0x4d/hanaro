# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from punit import theory, inlinedata
from hanaro import ConfigFilter


@theory
@inlinedata(True, 'test123', 'DEBUG', 'test123', logging.DEBUG, 'source and level match (not filtered)')
@inlinedata(True, 'test234', 'DEBUG', 'test123', logging.DEBUG, 'source does not match (not filtered)')
@inlinedata(False, 'test123', 'INFO', 'test123', logging.DEBUG, 'level below config (filtered)')
@inlinedata(True, 'test123', 'INFO', 'test123', logging.WARNING, 'level above config (not filtered)')
def matches_source_and_level(should_match: bool, source: str, level: str, name: str, levelno: int, reason: str) -> None:
    """Assert :class:``ConfigFilter`` will match *source* and *level* configuration settings."""
    record = logging.LogRecord(name, levelno, 'pathname', 5, 'msg', None, None, None, None)
    filter = ConfigFilter(
        "config_filter",
        {
            source: {
                'level': level
            }
        })
    is_match = filter.filter(record)
    assert is_match == should_match, reason


@theory
@inlinedata(True, 'neg', 'test', 'negative test')
@inlinedata(False, 'test', 'test', 'match sub-namespace')
@inlinedata(False, 'test.*', 'test.namespace', 'match sub-namespace')
@inlinedata(False, 'test.namespace', 'test.namespace', 'match exact')
@inlinedata(True, 'namespace', 'test.namespace', 'matches are left-aligned')
@inlinedata(False, '.*namespace', 'test.namespace', 'matches can be right-aligned')
@inlinedata(True, '.*name', 'test.namespace', 'matches cannot partially right-align')
@inlinedata(False, '.*name.*', 'test.namespace', 'matches can explicitly substring')
def regex_matching(should_match: bool, source: str, name: str, reason: str) -> None:
    """Assert :class:``ConfigFilter`` will match *source* having a regex patterns."""
    record = logging.LogRecord(name, logging.DEBUG, 'pathname', 5, 'msg', None, None, None, None)
    filter = ConfigFilter(
        "config_filter",
        {
            source: {
                'level': 'INFO',
                'regex': True
            }
        })
    is_match = filter.filter(record)
    assert is_match == should_match, reason


@theory
@inlinedata(True, 'neg', 'test', 'negative test')
@inlinedata(False, 'test', 'test', 'exact match')
@inlinedata(True, 'test.*', 'test.namespace', 'regex match should fail')
def non_regex_matching(should_match: bool, source: str, name: str, reason: str) -> None:
    """Assert :class:``ConfigFilter`` will match *source* NOT having a regex patterns."""
    record = logging.LogRecord(name, logging.DEBUG, 'pathname', 5, 'msg', None, None, None, None)
    filter = ConfigFilter(
        "config_filter",
        {
            source: {
                'level': 'INFO',
                'regex': False
            }
        })
    is_match = filter.filter(record)
    assert is_match == should_match, reason


@theory
@inlinedata(False, logging.DEBUG)
@inlinedata(False, logging.INFO)
@inlinedata(True, logging.WARN)
@inlinedata(True, logging.WARNING)
@inlinedata(True, logging.ERROR)
@inlinedata(True, logging.FATAL)
@inlinedata(True, logging.CRITICAL)
def level_matching(should_match: bool, level: int) -> None:
    """Assert :class:``ConfigFilter`` will match *level* setting."""
    record = logging.LogRecord('test', level, 'pathname', 5, 'msg', None, None, None, None)
    filter = ConfigFilter(
        "config_filter",
        {
            'test': {
                'level': 'WARNING'
            }
        })
    is_match = filter.filter(record)
    assert is_match == should_match
