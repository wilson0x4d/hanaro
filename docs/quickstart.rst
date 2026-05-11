Quick Start
============
.. _quickstart:


Installation
------------

**hanaro** can be installed from PyPI through the usual means:

.. code-block:: bash

    pip install hanaro


Usage
-----

Let's try a “learn by example” approach:

.. code-block:: python

    import hanaro
    hanaro.configure_logging()
    logger = hanaro.get_logger()
    logger.info('Hello, World!')

In the above example **hanaro** is used to apply a basic logging
configuration and then create a ``Logger`` instance that identifies the
current module. No explicit configuration is provided, so the default
behaviour is to allocate a *console* handler with a *logfmt* that allows
logging back‑ends (GTM, ELK, etc.) to properly handle multi‑line log
entries (typically error logs containing stack traces).

When executed the program outputs the following:

.. code-block:: plaintext

    [2025-12-31T12:34:56] Hello, World! level=INFO source=__main__


Configuration
-------------

Configuration handling is performed using
`appsettings2 <https://pypi.org/project/appsettings2/>`_ which supports
JSON, TOML, YAML, environment variables, and command‑line arguments to
provide a unified configuration.  For demonstration, assume the
following is the content of ``appsettings.json``:

.. code-block:: json

    {
        "logging": {
            "level": "INFO",
            "format": "[%(asctime)s] %(message)s level=%(levelname)s source=%(name)s %(metadata)s",
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
                    "format": "[%(asctime)s] level=%(levelname)s %(message)s source=\"%(name)s\" func=\"%(funcName)s\" %(metadata)s"
                },
                {
                    "type": "custom",
                    "class": "myapp.mymodule.myhandler",
                    "level": "WARNING",
                    "format": "msg=\"%(message)s\" level=\"%(levelname)s\" source=\"%(name)s\" func=\"%(funcName)s\" %(metadata)s"
                }
            ],
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
    }

Modifying the prior example to use such a configuration is trivial:

.. code-block:: python

    import appsettings2
    import hanaro

    hanaro.configure_logging(
        appsettings2.get_configuration()
    )
    logger = hanaro.get_logger()
    logger.info('Hello, World!')

QA and DevOps will find that
`appsettings2.get_configuration <https://appsettings2.readthedocs.io/en/latest/ref/helpers/get_configuration.html>`_
makes it very easy to override configuration with just the one line of
code.


Notables..
----------

* All configuration options are optional; you can reduce the config to
  specify only the features you wish to customize.
* If no configuration (or a partial configuration) is provided,
  ``configure_logging()`` will apply defaults.
* If no handlers are configured, a default handler for “console” logging
  is configured.
* If no format is specified, a default that is friendly toward GTM/ELK/etc.
  parsing is used.
* **hanaro** only has a single direct dependency:
  `appsettings2 <https://pypi.org/project/appsettings2/>`_.
