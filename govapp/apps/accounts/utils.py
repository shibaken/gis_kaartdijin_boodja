"""Kaartdijin Boodja Accounts Django Application Utility Functions."""


# Third-Party
from django import conf
from django.contrib import auth
from django.contrib.auth import models
from django.db.models import query

# Typing
from typing import Iterable, Union

from govapp import settings


# Shortcuts
UserModel = auth.get_user_model()


def all_administrators() -> Iterable[models.User]:
    """Retrieves all of the administrator users.

    Yields:
        models.User: Users in the administrator group.
    """
    # Retrieve and Yield
    yield from UserModel.objects.filter(
        groups__id=conf.settings.GROUP_ADMINISTRATOR_ID
    )


def all_catalogue_editors() -> Iterable[models.User]:
    """Retrieves all of the administrator users.

    Yields:
        models.User: Users in the administrator group.
    """
    # Retrieve and Yield
    yield from UserModel.objects.filter(
        groups__id=conf.settings.GROUP_CATALOGUE_EDITOR_ID
    )


def is_administrator(user: Union[models.User, models.AnonymousUser]) -> bool:
    """Checks whether a user is an Administrator.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Administrator group.
    """
    # Check and Return
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        and user.groups.filter(id=conf.settings.GROUP_ADMINISTRATOR_ID).exists()  # Must be in group
    )


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
        and user.groups.filter(id=conf.settings.GROUP_CATALOGUE_EDITOR_ID).exists()  # Must be in group
    )

def is_catalogue_admin(user: Union[models.User, models.AnonymousUser]) -> bool:
    # Check and Return
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        and user.groups.filter(name=settings.GROUP_CATALOGUE_ADMIN).exists()  # Must be in group
    )

def limit_to_administrators() -> query.Q:
    """Limits a fields choice to only objects in the Administrators group.

    Returns:
        query.Q: Query to limit object to those in the Administrators group.
    """
    # Construct Query and Return
    return query.Q(groups__pk=conf.settings.GROUP_ADMINISTRATOR_ID)


def limit_to_catalogue_editors() -> query.Q:
    """Limits a fields choice to only objects in the Catalogue Editors group.

    Returns:
        query.Q: Query to limit object to those in the Catalogue Editors group.
    """
    # Construct Query and Return
    return query.Q(groups__pk=conf.settings.GROUP_CATALOGUE_EDITOR_ID)
