from __future__ import annotations

import functools
import logging
import asyncio
from typing import Any, Callable, TypeVar, cast


F = TypeVar("F", bound=Callable[..., Any])


def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_function(logger: logging.Logger | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        active_logger = logger or get_logger(func.__module__)

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any):
                active_logger.info("Entering %s", func.__qualname__)
                try:
                    result = await func(*args, **kwargs)
                    active_logger.info("Completed %s", func.__qualname__)
                    return result
                except Exception:
                    active_logger.exception("Failed %s", func.__qualname__)
                    raise
                finally:
                    active_logger.info("Exiting %s", func.__qualname__)

            return cast(F, async_wrapper)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            active_logger.info("Entering %s", func.__qualname__)
            try:
                result = func(*args, **kwargs)
                active_logger.info("Completed %s", func.__qualname__)
                return result
            except Exception:
                active_logger.exception("Failed %s", func.__qualname__)
                raise
            finally:
                active_logger.info("Exiting %s", func.__qualname__)

        return cast(F, sync_wrapper)

    return decorator


def instrument_class_methods(cls: type[Any]) -> type[Any]:
    for name, value in list(cls.__dict__.items()):
        if name.startswith("__"):
            continue

        if isinstance(value, staticmethod):
            wrapped = log_function()(value.__func__)
            setattr(cls, name, staticmethod(wrapped))
            continue

        if isinstance(value, classmethod):
            wrapped = log_function()(value.__func__)
            setattr(cls, name, classmethod(wrapped))
            continue

        if callable(value):
            setattr(cls, name, log_function()(value))

    return cls


