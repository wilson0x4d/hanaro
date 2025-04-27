ConfigFilter
============

The ``ConfigFilter`` class facilitates filtering out unwanted logging output via configuration, it is not intended to be used directly (but can be if you need it.)

Typical Usage
-------------

Within a logging configuration there may be a ``filters`` section, for example:

.. code:: javascript

    "logging": {
        "filters": {
            "asyncio": {
                "level": "WARNING"
            },
            "mysql.*": {
                "level": "WARNING"
            },
            "urllib3.*": {
                "level": "WARNING"
            },
            "websockets.*": {
                "level": "WARNING"
            }
        }
    }

These result in individual `ConfigFilter` instances being created at runtime.

Each filter configuration has the following structure and options:

.. code:: javascript

    "source": {
        "level": 'DEBUG'|'INFO'|'WARN'|'WARNING'|'ERROR'|'FATAL'|'CRITICAL',
        "regex": true|false
    }

.. list-table::
    :widths: 25 50
    :header-rows: 0

    * - ``source``
      - **REQUIRED** The name of the Logger to filter, can be an exact match or a regex.
    * - ``level``
      - **OPTIONAL** The minimum logging Level required for logging Records to bypass the filter. Default is ``DEBUG``.
    * - ``regex``
      - **OPTIONAL** ``true`` if ``source`` is a regex, otherwise ``source`` is a literal string value. Default is ``true``.

Notes on Regex Support
----------------------

The regex support is Python's own pattern matching library (aka. `re`).

Provided regexes are clamped on the left and right side, ie. `^` and `$` specifiers are automatically applied. Thus, if you provide a value of ``'test'`` the resulting regex looks like ``'^test$'``.

The ``regex`` option allows regex support to be disabled if there is an undesired result, for example ``foo.bar`` unintentionally matching ``foo_bar`` because ``.`` is used for regex pattern matching.
