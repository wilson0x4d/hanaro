Quick Start
============
.. _quickstart:

.. contents::

Installation
------------

You can install **hanaro** from `PyPI <https://pypi.org/project/hanaro/>`_ using typical methods, such as ``pip``:

.. code:: bash

   pip install hanaro

Usage
-----

Let's try a "learn by example" approach. The following two snippets are the contents of a configuration file that contains a "logging" configuration section, and a Python code file that initializes Python's standard ``logging`` system using that configuration. This is by no means an exhaustive example, it only intends to touch on the major offerings of **hanaro**.

.. code:: javascript

    {
        "logging": {
            "level": "INFO",
            "format": "[%(asctime)s] %(message)s level=%(levelname)s source=%(name)s %(meta)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "handlers": [
                {
                    "type": "console",
                    "level": "DEBUG"
                },
                {
                    "type": "file",
                    "level": "DEBUG",
                    "path": "logs/",
                    "name": "debug.log",
                    "max_size": "4KiB",
                    "max_count": 10,
                    "format": "[%(asctime)s] level=%(levelname)s %(message)s source=\"%(name)s\" func=\"%(funcName)s\" %(meta)s"
                },
                {
                    "type": "custom",
                    "canonical": "myapp.mymodule.myhandler",
                    "level": "WARNING",
                    "format": "msg=\"%(message)s\" level=\"%(levelname)s\" source=\"%(name)s\" func=\"%(funcName)s\" %(meta)s"
                }
            ],
            "filters": {
                "asyncio": {
                    "level": "WARNING"
                },
                "mysql.connector": {
                    "level": "WARNING"
                },
                "urllib3.connectionpool": {
                    "level": "WARNING"
                },
                "websockets.client": {
                    "level": "WARNING"
                }
            }
        },
    }

This code sample is a minimum-viable solution. The ``custom`` handler above is omitted, but for the sake of demonstration know that ``canonical`` is the fully-qualified type name of a ``logging.Handler`` subclass and **hanaro** will create an instance of that class and configure as it does all other handlers.

.. code:: python

    from appsettings2 import getConfiguration
    from hanaro import configureLogging
    import logging

    configureLogging(getConfiguration())

    logger = logging.getLogger(__name__)

    logger.info('Hello, World!')

When executed the program outputs the following:

.. code:: plaintext
    
    [2025-12-31T12:34:56] Hello, World! level=INFO source=__main__ 

