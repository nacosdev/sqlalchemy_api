from sqlalchemy.sql.elements import KeyedColumnElement
from typing import Type, Optional


def get_column_python_type(column: KeyedColumnElement, only_type: bool = False) -> Type:
    """
    Get the python type of a SQLAlchemy column.

    Params:
    - `column`:  SQLAlchemy column
    - `only_type`: If True, only return the python type of the column, otherwise
        return the python type of the column wrapped in `Optional[]` if the column
        is nullable.
    """
    if hasattr(column.type, "impl"):
        if hasattr(column.type.impl, "python_type"):
            python_type = column.type.impl.python_type
    elif hasattr(column.type, "python_type"):
        python_type = column.type.python_type

    assert python_type, f"Could not infer python_type for {column}"

    if only_type:
        return python_type

    if column.nullable:
        python_type = Optional[python_type]

    return python_type
