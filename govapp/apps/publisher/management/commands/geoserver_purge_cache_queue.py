"""Kaartdijin Boodja Publisher Purge Cache Queue Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.publisher import geoserver_manager

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Execute PURGE_CACHE items in GeoServer Queue."""
    help = "Execute PURGE_CACHE items in the GeoServer Queue."

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        self.stdout.write("Executing PURGE_CACHE items in geoserver queue")
        geoserver_manager.GeoServerQueueExcutor().excute_purge_cache()
