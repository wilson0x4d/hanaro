`hanaro` (하나로) is a non-invasive `logging` configurator and facilitator for Python.

This README is only a high-level introduction to **hanaro**. For more detailed documentation, please view the official docs at [https://hanaro.readthedocs.io](https://hanaro.readthedocs.io).

## Installation

**hanaro** can be installed from pypi through the usual means:

```bash
pip install hanaro
```

## Usage

Let's try a "learn by example" approach. The following two snippets are the contents of a configuration file that contains a "logging" configuration section, and a Python code file that initializes Python's standard `logging` system using that configuration. This is by no means an exhaustive example, it only intends to touch on the major offerings of **hanaro**.

> NOTE: Configuration handling is performed using `appsettings2` which supports json, toml, yaml, xml, command-line args, and environment variables to provide a unified configuration solution. This example, however, uses json because of json's wider familiarity. For the sake of demonstration assume this content is in a file named `appsettings.json`.

```json
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
```

This code sample is a minimum-viable solution. The `custom` handler above is omitted, but for the sake of demonstration know that `canonical` is the fully-qualified type name of a `logging.Handler` subclass and **hanaro** will create an instance of that class and configure as it does all other handlers.

```python
from appsettings2 import getConfiguration
from hanaro import configureLogging
import logging

configureLogging(getConfiguration())

logger = logging.getLogger(__name__)

logger.info('Hello, World!')
```

When executed the program outputs the following:

```plaintext
[2025-12-31T12:34:56] Hello, World! level=INFO source=__main__ 
```

## Notables..

Things not obvious given the example above:

* All configuration options are optional, you can reduce the config to specifying only those things you wish to customize.
* It is not necessary to load a configuration at all, a call to `configureLogging()` will still apply reasonable defaults such as adding a console handler, applying a line format, applying a default date format (ISO 9601), etc.
* If no handlers are configured, a default handler for "console" is configured.

**hanaro** only has a single direct dependency: [``appsettings2``](https://pypi.org/project/appsettings2/).

## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/hanaro/issues/new/choose).
