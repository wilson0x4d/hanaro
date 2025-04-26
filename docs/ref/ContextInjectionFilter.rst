ContextInjectionFilter
======================

Facilitates injecting attributes into logging Records.

Initialization
--------------

.. py:currentmodule:: hanaro

.. py:class:: ContextInjectionFilter(context, isMetadata, metadataName)
    :canonical: hanaro.ContextInjectionFilter

    :param dict[str,str] context: The context to be injected. Each key of the dictionary representing one attribute to be injected into logging Records.
    :param bool isMetadata: (OPTIONAL) Indicates that the context should be aggregated into a single ``metadata`` attribute. Default is ``False``.
    :param str metadataName: (OPTIONAL) The name of the "meta" attribute. Default is ``metadata``.

What is the ``metadata`` attribute?
-----------------------------------

When configured, ``ContextInjectionFilter`` aggregates the ``context`` data into a single attribute named ``metadata``. This allows logging frameworks to control the position of metadata.

Why?
----

In some of our systems log processing divides into two major categories, metadata and messages. In those systems metadata is indexed whereas messages are non-indexed. Examples include LGTM, ELK, Splunk, others. Because of the way indexed metadata is used for searching, aggregation, and even trace correlation there is a natural incentive for programmers to emit metadata that is relevant to the activities of their programs.

One problem that arises is metadata invariance, ie. the metadata emitted by one component is not emitted by other components. This becomes an issue for logging frameworks which do not have a mechanism for writing arbitrary metadata, for example out of the box emitting attributes with Python's logging framework requires a custom format that includes all potential attributes.

Combined with the metadata invariance of components in a single program, or invariance among multiple programs within a cluster, defining formats that capture every possible attribute is impractical.

Typically programmers will overcome this problem by writing messages which include the metadata as part of the "message", while this may work, it has drawbacks:

* Reliability: Missing metadata can result in lost time or increased support costs when there is a problem.
* QOL: For metadata which is used for tracing/correlation, programmers are compelled to ensure necessary metadata appears in all affected log lines. This is a waste of their time, and a waste of their employer's money.

Another overlooked issue is that some systems expect metadata to appear positionally such as predicating message content, while others expect metadata to appear within specific delimiters like curly braces (sometimes both, positionally delimited.) When developers solve their indexing problems by emitting metadata as part of the message they risk building a solution that, eventually, cannot be easily integrated with systems that have  positional or structural requirements.

``ContextInjectionFilter`` metadata support solves these problems by collecting arbitrary attributes into a single attribute which can be configured one-time, and consistently, in the format of all logging output. This shifts the concern away from developers and over to operators responsible for managing log processing systems.


.. rubric:: Example:

.. code:: python

    from harano import ContextInjectionFilter
    import logging
    import uuid

    class Foo:
        def __init__(self) -> None:
            self.__oid = uuid.uuid4().hex
            self.__logger = logging.getLogger(__name__)
            self.__context = ContextInjectionFilter(isMetadata = True)
            self.__logger.addFilter(self.__context)
            self.__context['foo_id'] = self.__oid
            self.__callCounter = 0
        def doStuff(self) -> None:
            self.__callCounter += 1
            self.__context['call_id'] = str(self.__callCounter)
            try:
                self.__logger.info('Started processing..')
                # do stuff                
                self.__logger.info('Stopped processing..')
            finally:
                del self.__context['call_id']

    foo = Foo()
    foo.doStuff()
    foo.doStuff()
    foo.doStuff()

    # With a logging format of "{ %(metadata)s } %(message)s", outputs:
    #
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="1" } Started processing..
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="1" } Stopped processing..
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="2" } Started processing..
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="2" } Stopped processing..
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="3" } Started processing..
    # { foo_id="58722a4b3c8b448ba09cd07d061a1728" call_id="3" } Stopped processing..
    #

