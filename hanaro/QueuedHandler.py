# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
import queue


class QueuedHandler(logging.Handler):

    __s_queue:queue.Queue[logging.LogRecord] = queue.Queue()

    def __init__(self):
        super().__init__()

    def emit(self, record:logging.LogRecord) -> None:
        QueuedHandler.__s_queue.put(record)

    @staticmethod
    def getLogRecord() -> logging.LogRecord|None:
        record:logging.LogRecord = None
        try:
             record = QueuedHandler.__s_queue.get_nowait()
        except:
            pass
        return record
