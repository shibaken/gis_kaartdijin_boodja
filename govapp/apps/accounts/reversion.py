"""Kaartdijin Boodja Accounts Django Application Reversion Registry."""


# Third-Party
from django.contrib import auth
from django.contrib.auth import models
import reversion


# Shortcuts
UserModel = auth.get_user_model()
GroupModel = models.Group


# Register Models with Reversion
reversion.register(UserModel)
reversion.register(GroupModel)
