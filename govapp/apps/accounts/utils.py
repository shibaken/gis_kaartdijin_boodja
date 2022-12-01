"""Kaartdijin Boodja Accounts Django Application Utility Functions."""


# Third-Party
from django import conf
from django.contrib import auth
from django.contrib.auth import models

# Typing
from typing import Iterable


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
