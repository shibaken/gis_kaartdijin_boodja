"""Kaartdijin Boodja Publisher Django Application Configuration."""


# Third-Party
from django import apps


class PublisherConfig(apps.AppConfig):
    """Publisher Application Configuration."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "govapp.apps.publisher"
