from __future__ import annotations

from src.core.exceptions.base import BaseAppException


class InvalidSearchDataException(BaseAppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_SEARCH_DATA",
        )
