"""Kaartdijin Boodja Logs Django Application Configuration."""


# Third-Party
from django import apps


class LogsConfig(apps.AppConfig):
    """Logs Application Configuration."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "govapp.apps.logs"
