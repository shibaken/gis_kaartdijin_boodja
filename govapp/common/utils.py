"""Kaartdijin Boodja Django Application Utility Functions."""


# Third-Party
from functools import wraps
from django.db import models

# Typing
from typing import Any, Optional

import httpx


def filtered_manager(**kwargs: Any) -> models.manager.BaseManager:
    """Generates a Model Manager with the supplied filters applied.

    Args:
        **kwargs (Any): Filters to apply to the queryset.

    Returns:
        models.manager.BaseManager: Generated Filtered Manager.
    """
    # Construct Class
    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(**kwargs)

    # Return Manager
    return Manager()


def string_to_boolean(value: Optional[str]) -> bool:
    """Coerces a string value to a boolean.

    Returns:
        bool: The coerced boolean value.
    """
    # Parse and Return
    return True if value and value.lower() == "true" else False


def handle_http_exceptions(logger):
    """Decorator factory to handle HTTP exceptions and log them with the given logger."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                logger.error(f'HTTP status error in {func.__name__}: {e.response.status_code} {e.response.text}')
                raise
            except httpx.RequestError as exc:
                logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
                raise
            except httpx.RequestError as e:
                logger.error(f'Request error in {func.__name__}: {e}')
                raise
        return wrapper
    return decorator
