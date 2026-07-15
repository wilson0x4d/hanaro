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


@fact
def enter_returns_self() -> None:
    """Assert :meth:``__enter__`` returns the filter instance itself."""
    with ContextInjectionFilter({'key': 'val'}) as ctx:
        assert ctx is not None
        assert isinstance(ctx, ContextInjectionFilter)


@fact
def no_context_active_before_enter() -> None:
    """Assert no ContextInjectionFilter is active before any context manager is entered."""
    from hanaro.utils import _CIF_contextvar
    assert _CIF_contextvar.get() is None


@fact
def context_is_active_within_with_block() -> None:
    """Assert the ContextInjectionFilter is the active context inside a with block."""
    from hanaro.utils import _CIF_contextvar
    f = ContextInjectionFilter({'foo': 'bar'})
    with f:
        assert _CIF_contextvar.get() is f


@fact
def context_is_cleared_after_exit() -> None:
    """Assert the active context is restored to None after __exit__."""
    from hanaro.utils import _CIF_contextvar
    f = ContextInjectionFilter({'foo': 'bar'})
    with f:
        pass
    assert _CIF_contextvar.get() is None


@fact
def get_logger_in_context_attaches_filter() -> None:
    """Assert get_logger() attaches the active ContextInjectionFilter to the returned logger."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    f = ContextInjectionFilter({'foo': 'bar'})
    with f:
        logger = hanaro.get_logger()
        found = any(isinstance(filt, ContextInjectionFilter) and filt is f for filt in logger.filters)
        assert found, f'expected logger.filters to contain the ContextInjectionFilter instance, got: {logger.filters}'


@fact
def get_logger_outside_context_has_no_extra_filter() -> None:
    """Assert get_logger() does not attach a ContextInjectionFilter when no context is active."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    logger = hanaro.get_logger('test_no_context')
    cif_filters = [f for f in logger.filters if isinstance(f, ContextInjectionFilter)]
    assert len(cif_filters) == 0, f'expected no ContextInjectionFilter in logger.filters, got: {cif_filters}'


@fact
def nested_contexts_inner_has_inner_filter() -> None:
    """Assert nested context managers — inner scope has inner filter, outer scope has outer filter."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    from hanaro.utils import _CIF_contextvar
    outer = ContextInjectionFilter({'outer': 'yes'})
    inner = ContextInjectionFilter({'inner': 'yes'})
    with outer:
        assert _CIF_contextvar.get() is outer
        outer_logger = hanaro.get_logger('test_nested_outer')
        with inner:
            assert _CIF_contextvar.get() is inner
            inner_logger = hanaro.get_logger('test_nested_inner')
        assert _CIF_contextvar.get() is outer
        outer_logger2 = hanaro.get_logger('test_nested_outer2')
    assert _CIF_contextvar.get() is None
    assert outer_logger.filters[-1] is outer, f'outer_logger should have outer filter, got: {outer_logger.filters[-1]}'
    assert inner_logger.filters[-1] is inner, f'inner_logger should have inner filter, got: {inner_logger.filters[-1]}'


@fact
def log_record_receives_context_values() -> None:
    """Assert a LogRecord obtained via get_logger() inside a context receives injected values."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    f = ContextInjectionFilter({'request_id': 'abc-123'})
    with f:
        logger = hanaro.get_logger()
        # Capture the record by using a custom handler
        captured: list[logging.LogRecord] = []
        handler = logging.Handler()
        handler.emit = lambda record: captured.append(record)  # type: ignore[method-assign]
        logger.addHandler(handler)
        logger.info('test message')
        assert len(captured) == 1
        assert hasattr(captured[0], 'request_id')
        assert getattr(captured[0], 'request_id') == 'abc-123'


@fact
def attached_filter_is_same_instance() -> None:
    """Assert the filter attached to the logger is the same instance from the context."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    f = ContextInjectionFilter({'key': 'val'})
    with f:
        logger = hanaro.get_logger()
        found = any(filt is f for filt in logger.filters)
        assert found, f'expected logger.filters to contain the same ContextInjectionFilter instance'


@fact
def configure_logging_unchanged_by_context_manager() -> None:
    """Assert context manager usage does not interfere with configure_logging's handler-level filter."""
    import hanaro
    hanaro.configure_logging({'logging': {'handlers': [{'type': 'console'}]}})
    root = logging.getLogger()
    handler_filters = []
    for handler in root.handlers:
        handler_filters.extend(handler.filters)
    # Should have ConfigFilter and the shared ContextInjectionFilter from configure_logging
    assert any(isinstance(f, ContextInjectionFilter) for f in handler_filters), \
        f'expected configure_logging handler filter, got: {handler_filters}'

