Utils
=====

The utils module is where helper functions are located, for example ``configure_logging`` and ``get_queued_logger``.

.. py:function:: configure_logging(config)
    :canonical: hanaro.utils.configure_logging

    Configures Python's logging framework based on the provided configuration.

    :param appsettings2.Configuration config: (OPTIONAL) An ``appsettings2.Configuration`` to use for logging configuration. Default is ``None``.
    :returns: As a convenience, the list of logging Handlers which were configured, in case the calling application needs them for any reason.

.. rubric:: Example:

.. code:: python

    import hanaro

    hanaro.configure_logging()

    class Foo:
        def __init__(self) -> None:
            self.__logger = logging.getLogger('ur.special')
            self.__logger.info('Hello, World!')
    
    # Outputs to console (depends on format spec):
    # [2025-12-31 12:59:59] level=INFO name=ur.special Hello, World!

.. py:function:: get_logger(name,level)
    :canonical: hanaro.utils.get_logger

    Similar to Python's own ``logging.getLogger(...)`` except this function will attempt to resolve the name of the calling module when ``name`` is not provided.

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.

.. rubric:: Example:

.. code:: python

    import hanaro

    class Foo:
        def __init__(self) -> None:
            self.__logger = hanaro.get_logger()
            self.__logger.info('Hello, World!')

    # Outputs to console (depends on format spec):
    # [2025-12-31 12:59:59] level=INFO name=my.module Hello, World!
    

.. py:function:: get_queued_logger(name,level)
    :canonical: hanaro.utils.get_queued_logger

    Similar to Python's own ``logging.getLogger(...)`` except this function provides a bare-bones Logger that is only configured to forward logging Records to a :py:class:`~hanaro.QueuedHandler` (intentionally bypassing the rest of the logging system.)

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.

.. rubric:: Example:

.. code:: python

    import hanaro

    class Foo:
        def __init__(self) -> None:
            self.__logger = hanaro.get_queued_logger(__name__)
            self.__logger.info('Hello, World!')

    # Outputs to console:
    # (Nothing, because the logging record went into a queue.)
    # SEE ALSO: ``handle_queued_log_records()``

.. py:function:: handle_queued_log_records()
    :canonical: hanaro.utils.handle_queued_log_records

    Outputs all queued log records using the root logger.

.. rubric:: Example:

.. code:: python

    import hanaro

    hanaro.configure_logging({
        'logging': {
            'level': 'DEBUG',
            'handlers': [{'type':'console','level':'DEBUG'}]
        }
    })

    class Foo:
        def __init__(self) -> None:
            self.__logger = hanaro.get_queued_logger('ur.special')
            self.__logger.info('Hello, World!')
            hanaro.handle_queued_log_records()
    
    # Outputs to console (depends on format spec):
    # [2025-12-31 12:59:59] level="INFO" source="ur.special" msg="Hello, World!"
