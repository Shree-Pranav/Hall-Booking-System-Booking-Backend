from __future__ import annotations

from typing import Any


class BaseAppException(Exception):
    """Base exception for all custom application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to JSON-serializable dict."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }
