"""Kaartdijin Boodja Django Application Utility Functions."""


# Third-Party
from django.db import models

# Typing
from typing import Any, Optional


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
