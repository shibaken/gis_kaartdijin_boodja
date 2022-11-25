"""Kaartdijin Boodja Catalogue Django Application Utility Functions."""


# Third-Party
from django import conf
from django.contrib.auth import models
from rest_framework import request

# Local
from .models import catalogue_entries

# Typing
from typing import Optional, Union


def is_catalogue_editor(user: Union[models.User, models.AnonymousUser]) -> bool:
    """Checks whether a user is a Catalogue Editor.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Catalogue Editor group.
    """
    # Check and Return
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        and user.groups.filter(id=conf.settings.GROUP_CATALOGUE_EDITOR).exists()  # Must be in group
    )


def catalogue_entry_from_request(request: request.Request) -> Optional[catalogue_entries.CatalogueEntry]:
    """Retrieves a possible Catalogue Entry from request data.

    Args:
        request (request.Request): Request to retrieve Catalogue Entry from.

    Returns:
        Optional[catalogue_entries.CatalogueEntry]: Catalogue Entry.
    """
    # Retrieve Possible Catalogue Entry and Return
    return catalogue_entries.CatalogueEntry.objects.filter(
        id=request.data.get("catalogue_entry", -1),  # -1 Sentinel Value for Non-Existent Catalogue Entry
    ).first()
