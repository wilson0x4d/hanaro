# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from punit import fact
from hanaro import ContextInjectionFilter


@fact
def injects_context_values_into_logrecord() -> None:
    """Assert :class:``ContextInjectionFilter`` injects context values into Log Records."""
    record = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    filter = ContextInjectionFilter({
        'foo': 'bar',
        'bar': 'baz'
    })
    result = filter.filter(record)
    assert result is True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz'
    assert hasattr(record, 'metadata') is False


@fact
def injects_context_values_into_logrecord_as_metadata() -> None:
    """Assert :class:``ContextInjectionFilter`` injects context values into Log Records as a 'metadata' attribute."""
    record = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    filter = ContextInjectionFilter({
        'foo': 'bar',
        'bar': 'baz'
    }, is_metadata=True)
    result = filter.filter(record)
    assert result is True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz'
    assert hasattr(record, 'metadata')
    # NOTE: although this appears to check ordering, ordering is not guaranteed.
    assert getattr(record, 'metadata') == 'foo="bar" bar="baz"', f'expected=`foo="bar" bar="baz"`, actual=`{getattr(record, "metadata")}`'


@fact
def replaces_existing_attributes() -> None:
    """Assert :class:``ContextInjectionFilter`` replaces attributes in Log Record even if they already exist."""
    record: logging.LogRecord = logging.LogRecord('name', 3, 'pathname', 5, 'msg', None, None, None, None)
    # first filter
    filter1 = ContextInjectionFilter({
        'foo': 'bar1',
        'bar': 'baz1'
    }, is_metadata=True)
    result = filter1.filter(record)
    assert result is True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar1'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz1'
    assert hasattr(record, 'metadata')
    assert getattr(record, 'metadata') == 'foo="bar1" bar="baz1"', f'expected=`foo="bar1" bar="baz1"`, actual=`{getattr(record, "metadata")}`'
    # second filter
    filter2 = ContextInjectionFilter({}, is_metadata=True)
    # NOTE: this is done in this way for code coverage, it is functionally identical to the above forms
    filter2['bar'] = None
    filter2['foo'] = 'bar2'
    filter2['bar'] = 'baz2'
    filter2['bleh'] = 'tmp_blah1'
    filter2['bleh'] = None
    assert filter2['bleh'] is None
    filter2['bleh'] = 'tmp_blah2'
    del filter2['bleh']
    assert filter2['bleh'] is None
    filter2['bleh'] = 'blah'
    assert filter2['bleh'] == 'blah'
    result = filter2.filter(record)
    assert result is True
    assert hasattr(record, 'foo')
    assert getattr(record, 'foo') == 'bar2'
    assert hasattr(record, 'bar')
    assert getattr(record, 'bar') == 'baz2'
    assert hasattr(record, 'metadata')
    expected = 'foo="bar2" bar="baz2" bleh="blah"'
    assert getattr(record, 'metadata') == expected, f'expected=`{expected}`, actual=`{getattr(record, "metadata")}`'

