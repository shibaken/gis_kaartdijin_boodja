
"""Kaartdijin Boodja Publisher Scan Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.publisher import geoserver_manager

# Typing
from typing import Any

from govapp.apps.publisher.models.publish_channels import GeoServerPublishChannel


class Command(base.BaseCommand):
    # Help string
    help = "Excute Geoserver layer healthcheck"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Excuting geoserver layer healthcheck...")

        # Go!
        channels = GeoServerPublishChannel.objects.filter(active=True)
        for channel in channels:
            channel.perform_geoserver_layer_health_check()