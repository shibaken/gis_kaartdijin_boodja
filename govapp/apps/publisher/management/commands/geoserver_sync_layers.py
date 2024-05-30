"""Kaartdijin Boodja Publisher Scan Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.publisher import geoserver_manager

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Sync layers between Geoservers and GIS."""
    
    # Help string
    help = "Sync layers between Geoservers and GIS." 

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Starting to sync layers between GeoServers and GIS")

        # Go!
        # geoserver_queue_manager.GeoServerQueueExcutor().excute()
        geoserver_manager.GeoServerSyncExcutor().sync_deleted_layers()
        