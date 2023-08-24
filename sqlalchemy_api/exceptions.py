from typing import List


class InvalidOperator(ValueError):
    def __init__(
        self, operator: str, type_: type, column: str, valid_operators: List[str]
    ) -> None:
        self.operator = operator
        self.type_ = type_
        self.column = column
        self.valid_operators = valid_operators
        super().__init__(
            f"Invalid operator '{operator}' for type '{type_}' on column '{column}'. "
        )

    def errors(self):
        return [
            {
                "loc": ["query", self.column + "__" + self.operator],
                "msg": self.__str__(),
                "input": self.operator,
                "type": str(self.type_),
                "valid_operators": self.valid_operators,
            }
        ]


class NotFoundException(Exception):
    ...
