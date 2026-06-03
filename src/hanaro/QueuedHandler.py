# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
import queue


class QueuedHandler(logging.Handler):
    """
    Facilitates moving log output between threaded/async contexts via a Log Queue.

    An application that spawns background threads (such as asyncio event loops) eventually shows concurrency problems in logging output (partial stream writes, broken parsing in downstream systems, etc.)

    **QueuedHandler** solves concurrency problems by collecting Log Records to a thread-safe Log Queue, accessible from a single logging context (such as the main thread of an application) where it can be safely written in a way that preserves ordering and avoids multi-threaded clobbering of log output.
    """

    __s_queue: queue.Queue[logging.LogRecord] = queue.Queue()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a Log Record via the Log Queue.

        :param record: The Log Record to emit.
        """
        QueuedHandler.__s_queue.put(record)

    @staticmethod
    def get_log_record() -> logging.LogRecord | None:
        """
        Get a Log Record from the Log Queue.

        :return: A Log Record, or None if no Log Record is available.
        """
        try:
            return QueuedHandler.__s_queue.get_nowait()
        except Exception:
            pass  # NOP
        return None

    getLogRecord = get_log_record  # noqa: N815
    """⚠️ DEPRECATED: Use ``get_log_rewcord(...)`` instead."""
