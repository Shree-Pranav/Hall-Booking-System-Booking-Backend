from __future__ import annotations

from src.core.exceptions.base import BaseAppException


class GeneralAppException(BaseAppException):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "GENERAL_APPLICATION_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
        )
