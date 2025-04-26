Utils
=====

The utils module is where helper functions are located, for example ``configureLogging`` and ``getQueuedLogger``.

configureLogging
----------------

.. py:function:: configureLogging(config)
    :canonical: hanaro.utils.configureLogging

    Configures Python's logging framework based on the provided configuration.

    :param appsettings2.Configuration config: (OPTIONAL) An ``appsettings2.Configuration`` to use for logging configuration. Default is ``None``.
    :returns: As a convenience, the list of logging Handlers which were configured, in case the calling application needs them for any reason.


getQueuedLogger
---------------


.. py:function:: getQueuedLogger(name)
    :canonical: hanaro.utils.configureLogging

    Similar to Python's own ``logging.getLogger(...)`` except this function provides a bare-bones Logger that is only configured to forward logging Records to a :py:class:`~hanaro.QueuedHandler` (intentionally bypassing the rest of the logging system.)

    :param str name: (OPTIONAL) The name for the logger instance. Default is ``None``.
    :returns: A ``logging.Logger`` instance that only has a :py:class:`~hanaro.QueuedHandler` configured.



