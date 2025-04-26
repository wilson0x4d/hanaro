QueuedHandler
=============

``QueuedHandler`` facilitates moving log output between threaded/async contexts. For example, if you have an application that configures logging on the main thread and then spawns additional background threads (perhaps to establish multiple asyncio event loops) you will eventually observe concurrency problems emitting logging output.

``QueuedHandler`` solves that problem by aggregating logging Records into a thread-safe queue which can then be accessed from the main thread and dumped out to a single logging context.

This preserves the order of log lines, and also prevents some concurrency problems you may be experiencing. This is very much to cover an edge case that most developers will not experience.

Consider this "naive" example:

.. rubric:: Using QueuedHandler

.. code:: python

    import asyncio
    import harano
    import logging
    import random
    import uuid

    class MyWorker:
        def __init__(self) -> None:
            self.__logger = harano.getQueuedLogger(self.__class__.__name__)
            self.__logger.addFilter(harano.ContextInjectionFilter({ 'worker_id': uuid.uuid4().hex }))

        def __threadmain(self) -> None:
            self.__asyncioEventLoop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__asyncioEventLoop)
            self.__asyncioEventLoop.run_until_complete(self.__dowork())
            self.__logger.info(f'{self.__class__.__name__} stopped.')

        async def __dowork(self) -> None:
            counter = 0
            while True:
                counter += 1
                self.__logger.info(f'Worker Says: {counter}')
                async asyncio.sleep(0.1)

        def run(self) -> None:
            self.__thread = threading.Thread(target=self.__threadmain, daemon=True)
            self.__logger.info(f'{self.__class__.__name__} starting.')
            self.__thread.start()

    class MyApp:    
        def __init__(self) -> None:
            self.__logger = logging.getLogger(__name__)
            self.__workers = []

        def __createWorker(self) -> None:
            worker = MyWorker()
            self.__workers.append(worker)
            worker.run()

        async def run(self) -> None:
            while True:
                # do some stuff
                await asyncio.sleep(0.1)
                if len(self.__workers) < 10:
                    self.__createWorker()                
                # write queued logs
                while (logRecord := QueuedHandler.getLogRecord()) is not None:
                    self.__logger.callHandlers(logRecord)

    app = MyApp()
    asyncio.run(app.run())

    # The logging output might look something like:
    #
    # Worker Says: 1 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 2 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 1 worker_id="01200c3ff1684d139f52166b895509ce"
    # Worker Says: 3 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 2 worker_id="01200c3ff1684d139f52166b895509ce"
    # Worker Says: 4 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 1 worker_id="af4d0a8c4f7f44249c940bfb975e4f2f"
    # Worker Says: 3 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 2 worker_id="01200c3ff1684d139f52166b895509ce"
    # Worker Says: 4 worker_id="efc76cc1185c4ea58d2b2e6ce07959ed"
    # Worker Says: 2 worker_id="af4d0a8c4f7f44249c940bfb975e4f2f"
    # ..etc..
    #

As a final note; in the future a component responsible for collecting and dumping queued logging records may be added, especially if it is requested or the Community submits a PR for review. Currently we establish writers on an as-needed basis so one is not provided.
