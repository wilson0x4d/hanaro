# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from punit import *
from hanaro import ContextInjectionFilter

@fact
def recordShouldHaveContextAttributesInjected() -> None:
    record:logging.LogRecord = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    filter:ContextInjectionFilter = ContextInjectionFilter({
        'foo': 'bar',
        'bar': 'baz'
    })
    result = filter.filter(record)
    assert result == True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz'
    assert hasattr(record, 'metadata') == False

@fact
def recordShouldHaveMetadataInjectedWhenConfigured() -> None:
    record:logging.LogRecord = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    filter:ContextInjectionFilter = ContextInjectionFilter({
        'foo': 'bar',
        'bar': 'baz'
    }, isMetadata=True)
    result = filter.filter(record)
    assert result == True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz'
    assert hasattr(record, 'metadata')
    assert getattr(record, 'metadata') == f'foo="bar" bar="baz"', f'expected=`foo="bar" bar="baz"`, actual=`{getattr(record, 'metadata')}`'

@fact
def contextShouldReplaceDuplicateAttributes() -> None:
    record:logging.LogRecord = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    # first filter
    filter1:ContextInjectionFilter = ContextInjectionFilter({
        'foo': 'bar1',
        'bar': 'baz1'
    }, isMetadata=True)
    result = filter1.filter(record)
    assert result == True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar1'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz1'
    assert hasattr(record, 'metadata')
    assert getattr(record, 'metadata') == f'foo="bar1" bar="baz1"', f'expected=`foo="bar1" bar="baz1"`, actual=`{getattr(record, 'metadata')}`'
    # second filter
    filter2:ContextInjectionFilter = ContextInjectionFilter({
        'foo': 'bar2',
        'bar': 'baz2',
        'bleh': 'blah'
    }, isMetadata=True)
    result = filter2.filter(record)
    assert result == True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar2'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz2'
    assert hasattr(record, 'metadata')
    expected = f'foo="bar2" bar="baz2" bleh="blah"'
    assert getattr(record, 'metadata') == expected, f'expected=`{expected}`, actual=`{getattr(record, 'metadata')}`'

