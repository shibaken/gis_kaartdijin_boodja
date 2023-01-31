"""Kaartdijin Boodja Django Application Utility Functions."""


# Third-Party
from django.db import models

# Typing
from typing import Any


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
