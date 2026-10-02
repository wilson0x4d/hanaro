Configuration
=============

hanaro uses **`appsettings2`** as its configuration surface, so all logging settings can come from JSON, YAML, TOML, environment variables, or CLI arguments. All logging configuration lives under the ``logging`` key.

.. code:: javascript

    {
        "logging": {
            "level":     "DEBUG",
            "format":    "[%(asctime)s] %(message)s",
            "datefmt":   "%Y-%m-%dT%H:%M:%S",
            "bidi":      true,
            "allow_queued_logger": true,
            "filters":   {},
            "handlers":  []
        }
    }

Environment variable equivalent: ``LOGGING__LEVEL=WARNING``

Each top-level option is described below.

.. py:data:: logging__level

    Root logger level. Default is ``"DEBUG"``. Accepted values: ``"DEBUG"`` | ``"INFO"`` | ``"WARNING"`` | ``"ERROR"`` | ``"CRITICAL"``.

.. py:data:: logging__format

    Log message format string passed to ``logging.Formatter``. Default is Python's ``BASIC_FORMAT``.

.. py:data:: logging__datefmt

    Date format string passed to ``logging.Formatter``. Default is ``"%Y-%m-%dT%H:%M:%S"``.

.. _logging__bidi:

.. py:data:: logging__bidi

    Enable or disable the :py:class:`~hanaro.BidiFormatter` on all console handlers. Default is ``true``.
    Requires ``python-bidi`` to be installed.

    When ``true``:

    * ``BidiFormatter`` is automatically applied to any ``console`` handler in your logging config.
    * ``BidiFormatter`` is automatically applied to any ``logging.StreamHandler`` that does not have another formatter applied.
    * ``BidiFormatter`` is applied if a default logging configuration is used (i.e. no handlers configured).

    Disablement examples:

    .. code:: javascript

        {
            "logging": {
                "bidi": false
            }
        }

    .. code:: python

        from appsettings2 import get_configuration
        from hanaro import configure_logging

        configuration = get_configuration()
        configuration['logging__bidi'] = False

        configure_logging(configuration)

.. py:data:: logging__allow_queued_logger

    When ``true`` (default), :py:func:`~hanaro.get_logger` returns a :py:class:`~hanaro.QueuedHandler`-backed logger when called from non-main threads. Set to ``false`` to disable this behaviour.

.. py:data:: logging__filters

    A dictionary of filter rules. Each key is a logger name (exact string or regex pattern). See the **Filters** section below.

.. py:data:: logging__handlers

    A list of handler definitions. Each handler has a ``type`` field. See the **Handlers** section below.

Filters
-------

.. _Filters:

Each filter entry specifies a logger-name pattern and a minimum level:

.. code:: javascript

    "source": {
        "level": "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL",
        "regex": true | false
    }

* ``source`` (REQUIRED) The name of the logger to filter. Can be an exact match or a regex pattern.
* ``level`` (OPTIONAL) The minimum logging level required for log records to bypass the filter. Default is ``DEBUG``.
* ``regex`` (OPTIONAL) ``true`` if ``source`` is treated as a regex, otherwise it is a literal string. Default is ``true``.

Example configuration:

.. code:: javascript

    "logging": {
        "filters": {
            "asyncio":      { "level": "WARNING" },
            "mysql\\..*":   { "level": "ERROR" },
            "urllib3\\..*": { "level": "WARNING", "regex": false }
        }
    }

Regex notes
~~~~~~~~~~~

Regexes are implemented using Python's ``re`` module and are **auto-anchored**: ``^`` and ``$`` specifiers are applied automatically. A value of ``'test'`` becomes ``'^test$'``.

If there is an undesired result, set ``"regex": false`` to use literal matching instead. For example, ``foo.bar`` would unintentionally match ``foo_bar`` with regex (because ``.`` matches any character), but works as a literal match when ``regex`` is ``false``.

Handlers
--------

.. _Handlers:

The ``handlers`` list supports three handler ``type`` values:

+-------------+------------------------------------------+----------------------------------------+
| **type**    | **Required**                             | **Optional**                           |
+=============+==========================================+========================================+
| ``console`` | —                                        | ``level``, ``format``                  |
+-------------+------------------------------------------+----------------------------------------+
| ``file``    | —                                        | ``path``, ``name``, ``max_size``,      |
+-------------+------------------------------------------+----------------------------------------+
|             |                                          | ``max_count``                          |
+-------------+------------------------------------------+----------------------------------------+
| ``custom``  | ``class`` (fully-qualified class)        | ``level``, ``format``, ``args``        |
+-------------+------------------------------------------+----------------------------------------+

**Console handler** — writes to ``sys.stdout``.

.. code:: javascript

    {
        "type": "console",
        "level": "DEBUG"
    }

**File handler** — uses ``RotatingFileHandler`` with auto-rotation.

.. code:: javascript

    {
        "type": "file",
        "path": "logs/",                        // default: "logs"
        "name": "debug.log",                    // default: "<level>_<date>.log"
        "max_size": "4MiB",                     // default: 4MiB; supports KiB/MiB/GiB suffix
        "max_count": 10,                        // default: 10
        "level": "DEBUG",
        "format": "[%(asctime)s] %(message)s"
    }

**Custom handler** — import any ``logging.Handler`` subclass.

.. code:: javascript

    {
        "type": "custom",
        "class": "myapp.handlers.WebhookHandler",  // myapp/handlers.py: WebhookHandler(logging.Handler)
        "level": "ERROR",
        "format": "%(message)s",
        "args": { "url": "https://hooks.example.com" }  // passed as kwargs to the constructor
    }

Defaults Summary
----------------

+------------------+-----------------------------------------------------+
| Setting          | Default                                             |
+==================+=====================================================+
| Root level       | ``DEBUG``                                           |
+------------------+-----------------------------------------------------+
| Format           | Python's ``BASIC_FORMAT``                           |
+------------------+-----------------------------------------------------+
| Date format      | ``%Y-%m-%dT%H:%M:%S``                               |
+------------------+-----------------------------------------------------+
| Console handler  | Yes (if no handlers configured)                     |
+------------------+-----------------------------------------------------+
| Bidi support     | ``True`` (if ``python-bidi`` installed)             |
+------------------+-----------------------------------------------------+
| File max_size    | ``4MiB``                                            |
+------------------+-----------------------------------------------------+
| File max_count   | ``10``                                              |
+------------------+-----------------------------------------------------+
| File path        | ``logs/``                                           |
+------------------+-----------------------------------------------------+
| File name        | ``<level>_<date>.log``                              |
+------------------+-----------------------------------------------------+
