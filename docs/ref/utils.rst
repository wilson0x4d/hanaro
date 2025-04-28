Utils
=====

The utils module is where helper functions are located, for example ``configureLogging`` and ``getQueuedLogger``.

.. py:function:: configureLogging(config)
    :canonical: hanaro.utils.configureLogging

    Configures Python's logging framework based on the provided configuration.

    :param appsettings2.Configuration config: (OPTIONAL) An ``appsettings2.Configuration`` to use for logging configuration. Default is ``None``.
    :returns: As a convenience, the list of logging Handlers which were configured, in case the calling application needs them for any reason.

.. rubric:: Example:

.. code:: python

    import hanaro

    hanaro.configureLogging()

    class Foo:
        def __init__(self) -> None:
            self.__logger = logging.getLogger('ur.special')
            self.__logger.info('Hello, World!')
    
    # Outputs to console (depends on format spec):
    # [2025-12-31 12:59:59] level=INFO name=ur.special Hello, World!

.. py:function:: getLogger(name,level)
    :canonical: hanaro.utils.getLogger

    Similar to Python's own ``logging.getLogger(...)`` except this function will attempt to resolve the name of the calling module when ``name`` is not provided.

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.

.. rubric:: Example:

.. code:: python

    import hanaro

    class Foo:
        def __init__(self) -> None:
            self.__logger = hanaro.getLogger()
            self.__logger.info('Hello, World!')

    # Outputs to console (depends on format spec):
    # [2025-12-31 12:59:59] level=INFO name=my.module Hello, World!
    

.. py:function:: getQueuedLogger(name,level)
    :canonical: hanaro.utils.getQueuedLogger

    Similar to Python's own ``logging.getLogger(...)`` except this function provides a bare-bones Logger that is only configured to forward logging Records to a :py:class:`~hanaro.QueuedHandler` (intentionally bypassing the rest of the logging system.)

    :param str name: (OPTIONAL) The name for the logger instance. When not provided an attempt will be made to resolve the name of the calling module. Default is ``None``.
    :param int|str level: (OPTIONAL) The default logging Level for the Logger. Default is ```NOTSET```.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.

.. rubric:: Example:

.. code:: python

    import hanaro

    class Foo:
        def __init__(self) -> None:
            self.__logger = hanaro.getQueuedLogger(__name__)
            self.__logger.info('Hello, World!')

    # Outputs to console:
    # (Nothing, because the logging record went into a queue.)
