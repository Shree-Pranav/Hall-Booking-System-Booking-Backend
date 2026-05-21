"""Exception handlers for FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import BaseAppException
from src.observability.logging.logger import get_logger


ApplicationException = BaseAppException
logger = get_logger(__name__)


async def application_exception_handler(request: Request, exc: ApplicationException):
    """Handle custom application exceptions."""
    logger.error("Application exception handled: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error("Validation exception handled")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": [
                {
                    "field": " -> ".join(str(location) for location in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
                for err in exc.errors()
            ],
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception intercepted")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc) or "An unexpected error occurred",
            "error_type": "InternalServerError",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationException, application_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
