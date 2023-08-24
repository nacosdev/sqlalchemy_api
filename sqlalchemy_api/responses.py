from pydantic import BaseModel
from typing import Dict, List, Union, Any, Optional


class GenericResponse(BaseModel):
    content: Union[Dict, List, str, bytes]
    status_code: int
    media_type: str


class RowIDResponse(BaseModel):
    row_id: Any


class ErrorResponse(BaseModel):
    detail: Optional[List[Any]] = None
    message: Optional[str] = None


def error_response(
    detail: Optional[Any] = None, message: Optional[str] = None, status_code: int = 500
) -> GenericResponse:
    return GenericResponse(
        content=ErrorResponse(detail=detail, message=message).model_dump_json(
            exclude_none=True
        ),
        status_code=status_code,
        media_type="application/json",
    )


NOT_FOUND_RESPONSE = GenericResponse(
    content=ErrorResponse(message="Not found").model_dump_json(),
    status_code=404,
    media_type="application/json",
)
