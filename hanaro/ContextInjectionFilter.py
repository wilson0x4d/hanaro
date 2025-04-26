# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
import re


class ContextInjectionFilter(logging.Filter):

    def __init__(self, context:dict[str,str] = None, isMetadata:bool = False, metadataName:str = 'metadata'):
        self.__context = context if context is not None else {}
        self.__isMetadata = isMetadata
        self.__metadataName = metadataName if metadataName is not None and len(metadataName) > 0 else 'metadata'
        super().__init__()

    def __getitem__(self, key:str) -> str|None:
        self.__context.get(key, None)

    def __setitem__(self, key:str, value:str|None) -> None:        
        self.__context[key] = value

    def __delitem__(self, key:str) -> None:
        self.__context.pop(key, None)

    def filter(self, record:logging.LogRecord) -> bool:
        if self.__isMetadata:
            metadata = f' {getattr(record, self.__metadataName, '')}'
            for k,v in self.__context.items():
                if not hasattr(record, k):
                    metadata = f'{metadata} {k}="{v}"'
                else:
                    metadata = re.sub(f' {k}="[^"]*"', f' {k}="{v}"', metadata)
                setattr(record, k, v)
            setattr(record, self.__metadataName, metadata.lstrip())
        else:            
            for k,v in self.__context.items():
                setattr(record, k, v)
        return True
