# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from hanaro import QueuedHandler, getQueuedLogger
from hanaro.utils import handleQueuedLogRecords
import logging
from punit import fact


@fact
async def queuedLogger_bvt() -> None:
    expected_count = 10
    logger = getQueuedLogger()
    async def emitter() -> None:
        emission_count = 0
        for i in range(0,expected_count):
            emission_count += 1
            logger.debug(f'queued emission: {emission_count}')
    await emitter()
    actual_count = 0
    while (logRecord := QueuedHandler.getLogRecord()) is not None:
        if 'queued emission' in logRecord.getMessage():
            actual_count += 1
    assert actual_count == expected_count, f'expected{expected_count}, actual:{actual_count}'
    # NOTE: these two lines only exist for code coverage, the above validated functionality.
    logger.debug(f'coverage')
    handleQueuedLogRecords()
