"""Kaartdijin Boodja Publisher Scan Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.publisher import geoserver_queue_manager

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Excute itemes in GeoServer Queue model."""
    # Help string
    help = "Excute itemes that pushed in GeoServer Queue(DB table)." 

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Excuting items of geoserver queue")

        # Go!
        geoserver_queue_manager.excute()

