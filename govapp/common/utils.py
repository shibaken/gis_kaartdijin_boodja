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


def calculate_dict_differences(dict1, dict2):
    """
    Calculate items that are common to both dictionaries (with the same values)
    and items that are only contained in one of the dictionaries.

    :param dict1: First dictionary
    :param dict2: Second dictionary
    :return: Tuple of three dictionaries: common_items, dict1_only_items, dict2_only_items
    """
    
    # Calculate common keys between both dictionaries
    common_keys = set(dict1.keys()) & set(dict2.keys())

    # Calculate common items (with the same values in both dictionaries)
    common_items = {key: dict1[key] for key in common_keys if dict1[key] == dict2[key]}

    # Calculate items present only in dict1
    dict1_only_items = {key: dict1[key] for key in set(dict1.keys()) - set(dict2.keys())}

    # Calculate items present only in dict2
    dict2_only_items = {key: dict2[key] for key in set(dict2.keys()) - set(dict1.keys())}

    return common_items, dict1_only_items, dict2_only_items
