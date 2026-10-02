# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT
from __future__ import annotations

import contextvars
import logging
import re
from typing import Optional


class ContextInjectionFilter(logging.Filter):
    """
    Injects context data into Log Records.

    This filter can operate in two modes: as a regular context injector that sets
    individual attributes on each Log Record, or as a metadata injector that
    consolidates all context values into a single metadata attribute.

    Usage
    -----

    .. code-block:: python

        with ContextInjectionFilter({'request_id': 'abc-123'}) as ctx:
            logger = get_logger()
            logger.info('request processing')
    """

    __token: contextvars.Token[Optional[ContextInjectionFilter]] | None

    def __init__(self, context: Optional[dict[str, str]] = None, is_metadata: bool = False, metadata_name: str = 'metadata'):
        """
        Initialize a *ContextInjectionFilter* with the specified values.

        :param context: A baseline context dictionary to be injected into affected Log Records.
        :param is_metadata: Indicates that the context being injected is a "metadata" context.
        :param metadata_name: For "metadata" contexts, sets the Log Record Attribute Name of the metadata, defaults to "metadata".
        """
        self.__context = context if context is not None else {}
        self.__is_metadata = is_metadata
        self.__metadata_name = (
            metadata_name
            if metadata_name is not None and len(metadata_name) > 0
            else 'metadata'
        )
        super().__init__()
        self.__token = None


    def __getitem__(self, key: str) -> str | None:
        """
        Get a value for the specified *key* from the context.

        :param key: The key to get the value of.
        :returns: The value if one is found, otherwise ``None``.
        """
        return self.__context.get(key, None)

    def __setitem__(self, key: str, value: str | None) -> None:
        """
        Set a *value* for the specified *key* in the context.

        :param key: The key to set the value of.
        :param value: The value to be set. If ``None`` then *key* is removed from the context entirely.
        """
        if value is None:
            if key in self.__context:
                del self.__context[key]
        else:
            self.__context[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Delete the value for the specified *key*.

        :param key: The key to delete the value of.
        """
        self.__context.pop(key, None)

    def __enter__(self) -> ContextInjectionFilter:
        """
        Establish this filter as the active context.

        Any :py:func:``get_logger()`` call within this context will
        automatically attach this filter to the returned logger.

        :returns: ``self`` so it can be assigned in a ``with`` statement.
        """
        from .utils import _CIF_contextvar
        self.__token = _CIF_contextvar.set(self)
        return self

    def __exit__(self, *args: object) -> None:
        """
        Restore the previous :py:class:``ContextInjectionFilter`` from
        the enclosing scope.
        """
        from .utils import _CIF_contextvar
        if self.__token is not None:
            _CIF_contextvar.reset(self.__token)
            self.__token = None

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Mutates *record* by setting context values as attributes.

        If this is a "metadata" context then the values are consolidated
        into a single "metadata attribute" instead.

        :param record: The Log Record to mutate.
        :returns: ``True``
        """
        if self.__is_metadata:
            metadata = f' {getattr(record, self.__metadata_name, "")}'
            for k, v in self.__context.items():
                if not hasattr(record, k):
                    metadata = f'{metadata} {k}="{v}"'
                else:
                    metadata = re.sub(f' {k}="[^"]*"', f' {k}="{v}"', metadata)
                setattr(record, k, v)
            setattr(record, self.__metadata_name, metadata.lstrip())
        else:
            for k, v in self.__context.items():
                setattr(record, k, v)
        return True
