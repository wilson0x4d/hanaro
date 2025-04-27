# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
import re


class _ConfigFilterSettings:

    level:str
    pattern:re.Pattern|None
    regex:bool
    source:str

    def __init__(self, source:str, settings:dict[str,str]):
        self.source = source
        self.regex = settings.get("regex", True)
        self.level = getattr(logging, settings.get("level", "DEBUG").upper())
        self.pattern = None if not self.regex else re.compile(f'^{source}$', re.RegexFlag.IGNORECASE)


class ConfigFilter(logging.Filter):

    def __init__(self, config:dict[str,dict[str,str]]):
        self.__settings = [_ConfigFilterSettings(k, v) for k,v in config.items()]
        super().__init__()

    def filter(self, record:logging.LogRecord) -> bool:
        for e in self.__settings:
            isMatch = (record.name == e.source) if e.pattern is None else (e.pattern.match(record.name))
            if isMatch and record.levelno < e.level:
                return False
        return True
