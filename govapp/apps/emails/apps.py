"""Kaartdijin Boodja Emails Django Application Configuration."""


# Third-Party
from django import apps


class EmailsConfig(apps.AppConfig):
    """Emails Application Configuration."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "govapp.apps.emails"
