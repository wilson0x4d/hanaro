# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from punit import *
from hanaro import ConfigFilter

@theory
@inlinedata(True, 'test123', 'DEBUG', 'test123', logging.DEBUG, 'source and level match (not filtered)')
@inlinedata(True, 'test234', 'DEBUG', 'test123', logging.DEBUG, 'source does not match (not filtered)')
@inlinedata(False, 'test123', 'INFO', 'test123', logging.DEBUG, 'level below config (filtered)')
@inlinedata(True, 'test123', 'INFO', 'test123', logging.WARNING, 'level above config (not filtered)')
def shouldMatchSourceAndLevel(expected:bool, source:str, level:str, name:str, levelno:int, reason:str) -> None:
    record:logging.LogRecord = logging.LogRecord(name, levelno, 'pathname', 5, 'msg', None, None, None, None)
    filter:ConfigFilter = ConfigFilter({
        source: {
            'level': level
        }
    })
    result = filter.filter(record)
    assert result == expected, reason

@theory
@inlinedata(True, 'neg', 'test', 'negative test')
@inlinedata(False, 'test', 'test', 'match sub-namespace')
@inlinedata(False, 'test.*', 'test.namespace', 'match sub-namespace')
@inlinedata(False, 'test.namespace', 'test.namespace', 'match exact')
@inlinedata(True, 'namespace', 'test.namespace', 'matches are left-aligned')
@inlinedata(False, '.*namespace', 'test.namespace', 'matches can be right-aligned')
@inlinedata(True, '.*name', 'test.namespace', 'matches cannot partially right-align')
@inlinedata(False, '.*name.*', 'test.namespace', 'matches can explicitly substring')
def supportsRegexMatching(expected:bool, source:str, name:str, reason:str) -> None:
    record:logging.LogRecord = logging.LogRecord(name, logging.DEBUG, 'pathname', 5, 'msg', None, None, None, None)
    filter:ConfigFilter = ConfigFilter({
        source: {
            'level': 'INFO',
            'regex': True
        }
    })
    result = filter.filter(record)
    assert result == expected, reason

@theory
@inlinedata(True, 'neg', 'test', 'negative test')
@inlinedata(False, 'test', 'test', 'exact match')
@inlinedata(True, 'test.*', 'test.namespace', 'regex match should fail')
def supportsNonRegexMatching(expected:bool, source:str, name:str, reason:str) -> None:
    record:logging.LogRecord = logging.LogRecord(name, logging.DEBUG, 'pathname', 5, 'msg', None, None, None, None)
    filter:ConfigFilter = ConfigFilter({
        source: {
            'level': 'INFO',
            'regex': False
        }
    })
    result = filter.filter(record)
    assert result == expected, reason


@theory
@inlinedata(False, logging.DEBUG)
@inlinedata(False, logging.INFO)
@inlinedata(True, logging.WARN)
@inlinedata(True, logging.WARNING)
@inlinedata(True, logging.ERROR)
@inlinedata(True, logging.FATAL)
@inlinedata(True, logging.CRITICAL)
def loggingLevelBasicVerification(expected:bool, levelno:int) -> None:
    record:logging.LogRecord = logging.LogRecord('test', levelno, 'pathname', 5, 'msg', None, None, None, None)
    filter:ConfigFilter = ConfigFilter({
        'test': {
            'level': 'WARNING'
        }
    })
    result = filter.filter(record)
    assert result == expected
