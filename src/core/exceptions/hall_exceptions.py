from src.core.exceptions.base import BaseAppException


class HallNotFoundException(BaseAppException):
    """Exception raised when a hall is not found."""

    def __init__(self, message: str = "Hall not found") -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="HALL_NOT_FOUND",
        )


class ResourceNotFoundError(BaseAppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
        )


class UnauthorizedException(BaseAppException):
    """Exception raised when user is not authorized."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="UNAUTHORIZED",
        )


class InvalidTokenException(BaseAppException):
    """Exception raised when token is invalid."""

    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_TOKEN",
        )
