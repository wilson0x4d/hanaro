BidiFormatter
=============

The ``BidiFormatter`` class facilitates bidirection text display (ie. properly rendering RTL on LTR displays and vice versa).

Default Behaviors
-----------------

If the `pybidi` module/library is detected..

- `BidiFormatter` will be automatically applied to any `console` handler in your logging config.
- `BidiFormatter` will be automatically applied to any `logging.Streamhandler` that does not have another formatter applied.
- `BidiFormatter` will be automatically applied if a 'default' logging configuration is used (ie. when you provided no custom configuration.)

The easiest way to opt-in is to install the ``bidi`` extra:

.. code:: bash

    pip install hanaro[bidi]

Disablement via Config
----------------------

If you have `pybidi` installed but do NOT want it being applied by default, you can explicitly disable the functionality via config:

.. code:: javascript

    {
        "logging": {
            "bidi": false
        }
    }

Disablement via Code
--------------------

If you have `pybidi` installed but do NOT want it being applied by default, you can explicitly disable the functionality via code:


.. code:: python

    from appsettings2 import getConfiguration
    from hanaro import configureLogging

    configuration = getConfiguration()
    configuration['logging__bidi'] = False

    configureLogging(configuration)

Explicit Configuration
----------------------

The ``BidiFormatter`` can also be manually injected at run-time where it is needed, just like the default ``logging.Formatter``.
