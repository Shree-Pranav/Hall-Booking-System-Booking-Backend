from __future__ import annotations

from src.core.exceptions.base import BaseAppException


class BookingNotFoundException(BaseAppException):
    def __init__(self, message: str = "Booking not found") -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="BOOKING_NOT_FOUND",
        )


class BookingForbiddenException(BaseAppException):
    def __init__(self, message: str = "You are not allowed to modify this booking") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="BOOKING_FORBIDDEN",
        )


class BookingConflictException(BaseAppException):
    def __init__(self, message: str = "Booking conflict") -> None:
        super().__init__(
            message=message,
            status_code=409,
            error_code="BOOKING_CONFLICT",
        )


class InvalidBookingDataException(BaseAppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_BOOKING_DATA",
        )
