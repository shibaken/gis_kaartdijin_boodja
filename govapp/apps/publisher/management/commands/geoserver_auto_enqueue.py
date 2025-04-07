"""Kaartdijin Boodja Publisher Auto Enqueue Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.publisher import geoserver_manager

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Automatically enqueue eligible items to GeoServer Queue."""
    # Help string
    help = "Automatically enqueue eligible items to the GeoServer Queue for processing."

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Starting automatic enqueue process for GeoServer queue")

        # Go!
        geoserver_manager.GeoServerQueueExcutor().auto_enqueue()
