"""Kaartdijin Boodja Catalogue Django Application Utility Functions."""


# Third-Party
from django import conf
from django.contrib.auth import models

# Typing
from typing import Union


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
