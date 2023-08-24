from enum import Enum


class Actions(Enum):
    CREATE = "CREATE"
    CREATE_MANY = "CREATE_MANY"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    GET = "GET"
    GET_MANY = "GET_MANY"


ALL_ACTIONS = [action for action in Actions]
