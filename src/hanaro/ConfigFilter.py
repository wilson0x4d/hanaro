# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
import re
from typing import Any, cast


class _ConfigFilterSettings:

    level:int
    pattern:re.Pattern|None
    regex:bool
    source:str

    def __init__(self, source:str, settings:dict[str,str]) -> None:
        self.source = source
        s = settings.get('regex', True)
        self.regex = s == 'True' or s == True
        self.level = cast(int, getattr(logging, settings.get('level', 'DEBUG').upper()))
        self.pattern = None if not self.regex else re.compile(f'^{source}$', re.RegexFlag.IGNORECASE)


class ConfigFilter(logging.Filter):

    def __init__(self, name:str = '', config:dict[str,dict[str,Any]] = {}) -> None:
        self.__settings = [_ConfigFilterSettings(k, v) for k,v in config.items()]
        super().__init__(name)

    def filter(self, record:logging.LogRecord) -> bool:
        for e in self.__settings:
            isMatch = (record.name == e.source) if e.pattern is None else (e.pattern.match(record.name))
            if isMatch and record.levelno < e.level:
                return False
        return True
