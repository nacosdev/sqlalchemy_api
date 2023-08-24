from typing import Optional, Any, List
from sqlalchemy.sql.elements import KeyedColumnElement
from datetime import date, datetime
import enum

IS_NULL = "is_null"
IS_NOT_NULL = "is_not_null"

NULL_OPERATORS = [
    IS_NULL,
    IS_NOT_NULL,
]

BASE_OPERATORS = [
    *NULL_OPERATORS,
    "equal",
    "ne",
]

NUMERIC_OPERATORS = [
    *BASE_OPERATORS,
    "gt",
    "ge",
    "lt",
    "le",
]

STRING_OPERATORS = [
    *BASE_OPERATORS,
    "contains",
    "startswith",
    "endswith",
]

TYPE_OPERATORS = {
    str: STRING_OPERATORS,
    int: NUMERIC_OPERATORS,
    float: NUMERIC_OPERATORS,
    bool: NUMERIC_OPERATORS,
    datetime: NUMERIC_OPERATORS,
    date: NUMERIC_OPERATORS,
    enum: STRING_OPERATORS,
}


OPERATOR_ATTR_MAP = {
    "equal": "__eq__",
    "ne": "__ne__",
    "gt": "__gt__",
    "ge": "__ge__",
    "lt": "__lt__",
    "le": "__le__",
    "contains": "contains",
    "startswith": "startswith",
    "endswith": "endswith",
}


class Filter:
    def __init__(
        self,
        name: str,
        type_: type,
        nullable: bool,
        column: KeyedColumnElement,
        default: Optional[Any] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.type = type_
        self.nullable = nullable
        self.column = column
        self.default = default
        self.description = description

    @property
    def operator_name(self) -> str:
        return self.name + "__op"

    @property
    def operators(self) -> List[str]:
        if self.type in TYPE_OPERATORS:
            operations = TYPE_OPERATORS[self.type]
            if not self.nullable:
                operations = [op for op in operations if op not in NULL_OPERATORS]
            return operations
        return BASE_OPERATORS
