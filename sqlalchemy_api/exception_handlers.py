from typing import Callable, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy_api.responses import GenericResponse, error_response
from sqlalchemy_api.exceptions import NotFoundException
from pydantic_core import ValidationError
import json
import traceback


def unhandled_exception_response(exc: Exception, debug: bool) -> GenericResponse:
    content: Any = {"detail": "Internal server error"}
    if debug:
        content = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ).split("\n")
    return GenericResponse(
        content=json.dumps(content),
        status_code=500,
        media_type="application/json",
    )


def handle_integrity_error(exc: IntegrityError, *args) -> GenericResponse:
    return error_response(
        message="Integrity error",
        detail=[
            {
                "exception_type": "IntegrityError",
                "description": str(exc.orig).split("\n"),
            }
        ],
        status_code=409,
    )


def handle_not_found_error(*args) -> GenericResponse:
    return error_response(message="Not found", status_code=404)


def validation_error_handler(exc: ValidationError, *args) -> GenericResponse:
    return error_response(
        detail=exc.errors(),
        status_code=422,
    )


exception_handlers: Dict[
    Any,
    Callable[[Any, bool], GenericResponse],
] = {
    IntegrityError: handle_integrity_error,
    NotFoundException: handle_not_found_error,
    ValidationError: validation_error_handler,
}
