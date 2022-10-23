"""Kaartdijin Boodja Swagger UI Django Application Configuration."""


# Third-Party
from django import apps


class SwaggerConfig(apps.AppConfig):
    """Swagger Application Configuration."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "govapp.apps.swagger"
