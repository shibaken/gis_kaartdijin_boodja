"""Kaartdijin Boodja Catalogue Django Application Configuration."""


# Third-Party
from django import apps
from django.db.models.signals import post_migrate

class CatalogueConfig(apps.AppConfig):
    """Catalogue Application Configuration."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "govapp.apps.catalogue"
    
    def ready(self):
        from govapp.apps.catalogue.models.layer_attribute_types import add_initial_types
        post_migrate.connect(add_initial_types, sender=self)
