"""Kaartdijin Boodja Logs Django Application Utility Functions."""


# Third-Party
from django.db import models
from django.contrib.auth import models as auth_models

# Local
from govapp.apps.logs import models as logs_models

# Typing
from typing import Union


def add_to_actions_log(
    user: Union[auth_models.User, auth_models.AnonymousUser],
    model: models.Model,
    action: str,
) -> logs_models.ActionsLogEntry:
    """Adds an Actions Log entry for the specified model.

    Args:
        user (Union[auth_models.User, auth_models.AnonymousUser]): User to
            attribute this actions Log entry to.
        model (models.Model): Model for the actions log entry.
        action (str): Content of the actions log entry.

    Returns:
        logs_models.ActionsLogEntry: The created actions log entry.
    """
    # Create and Return Actions Log Entry
    return logs_models.ActionsLogEntry.objects.create(
        content_object=model,  # type: ignore
        who=user,
        what=action,
    )
