import ipaddress
import uuid
from typing import Any

import sqlalchemy
from orjson import loads

from saffier.sqlalchemy.protocols import BaseFieldProtocol
from saffier.sqlalchemy.types import SubList
from saffier.types import DictAny

DIALECTS = {"postgres": "postgres"}


class GUIDField(BaseFieldProtocol):
    """
    GUID type representation.
    """

    impl: Any = sqlalchemy.CHAR
    cache_ok: bool = True

    def load_dialect_impl(self, dialect: Any):
        if dialect.name != DIALECTS["postgres"]:
            return dialect.type_descriptor(sqlalchemy.CHAR(32))
        return dialect.type_descriptor(sqlalchemy.dialects.postgresql.UUID())

    def process_bind_param(self, value: Any, dialect: Any) -> str:
        if value is None:
            return value
        if dialect.name != DIALECTS["postgres"]:
            return value.hex
        return str(value)

    def process_result_value(self, value: Any, dialect: Any):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


class IPField(BaseFieldProtocol):
    """
    Representation of an IP field.
    """

    impl: str = sqlalchemy.CHAR
    cache_ok: bool = True

    def load_dialect_impl(self, dialect: Any):
        if dialect.name != DIALECTS["postgres"]:
            return dialect.type_descriptor(sqlalchemy.CHAR(45))
        return dialect.type_descriptor(sqlalchemy.dialects.postgresql.INET())

    def process_bind_param(self, value: Any, dialect: Any) -> str:
        if value is not None:
            return str(value)

    def process_result_value(self, value: Any, dialect: Any):
        if value is None:
            return value
        if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            value = ipaddress.ip_address(value)
        return value


class ListField(BaseFieldProtocol):
    """
    Representation of a List.
    """

    def __init__(
        self, impl: str = sqlalchemy.TEXT, cache_ok: bool = True, **kwargs: DictAny
    ) -> None:
        self.delimiter = kwargs.pop("delimiter", ",")
        super().__init__(**kwargs)
        self.impl = impl
        self.cache_ok = cache_ok

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name != DIALECTS["postgres"]:
            return dialect.type_descriptor(sqlalchemy.CHAR(5000))
        return dialect.type_descriptor(sqlalchemy.dialects.postgresql.VARCHAR())

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is not None:
            value = loads(value)
            return list(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return SubList(self.delimiter)
        if isinstance(value, list):
            return value
        return SubList(self.delimiter, value.split(self.delimiter))
