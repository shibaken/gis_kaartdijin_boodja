"""Kaartdijin Boodja Logs Django Application Utility Functions."""


# Third-Party
from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib import auth

# Local
from govapp.apps.logs import models as logs_models

# Typing
from typing import Union


def add_to_actions_log(
    user: Union[auth_models.User, auth_models.AnonymousUser],
    model: models.Model,
    action: str,
    default_to_system: bool = False,
) -> logs_models.ActionsLogEntry:

    if user is None and default_to_system:
        UserModel = auth.get_user_model()
        system_email = 'gis_system@dbca.wa.gov.au'
        first_name = 'GIS'
        last_name = 'System'
        
        try:
            user = UserModel.objects.get(email=system_email)
        except (UserModel.DoesNotExist, auth_models.user.DoesNotExist):
            user = UserModel.objects.create_user(
                username=system_email,
                email=system_email,
                password=UserModel.objects.make_random_password(),
                is_staff=True,
                is_superuser=False,
                first_name=first_name,
                last_name=last_name,
            )

    # Create and Return Actions Log Entry
    return logs_models.ActionsLogEntry.objects.create(
        content_object=model,  # type: ignore
        who=user,
        what=action,
    )
