"""Kaartdijin Boodja Catalogue Django Application Utility Functions."""


# Standard
import hashlib
import json

# Third-Party
from django.db import models

# Typing
from typing import Any, Iterable, Optional


def attributes_hash(attributes: Optional[Iterable[Any]]) -> str:
    """Calculates the hash of attributes.

    This function heavily relies on Python duck-typing - i.e., you can call
    this function with an iterable of *any* object, and the function will
    attempt to make it work. This was done so that Django models and
    dataclasses can both be passed in.

    This function is used to determine whether the Catalogue Entry matches its
    active Layer Submission at runtime.

    Args:
        attributes (Optional[Iterable[Any]]): Possible iterable of attributes.

    Returns:
        str: The hex SHA256 hash of the attributes.
    """
    # Initialise Hash
    hash = hashlib.sha256()  # noqa: A001

    # Allow the iteration below in the case that there are no attributes
    attributes = attributes or []

    # Loop through attributes in order
    # We expect the attributes to have an `order` field
    # If not, we leave them sorted as is
    for attribute in sorted(attributes, key=lambda a: getattr(a, "order", 0)):
        # Construct attribute dictionary
        attr = {
            "name": getattr(attribute, "name", None),
            "type": getattr(attribute, "type", None),
            "order": getattr(attribute, "order", None),
        }

        # Serialize attribute dictionary to JSON and encode the JSON
        json_string = json.dumps(attr, sort_keys=True, default=str)
        json_bytes = json_string.encode("UTF-8")

        # Update Hash
        hash.update(json_bytes)

    # Return
    return hash.hexdigest()


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
