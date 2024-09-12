from django.core.management import base
from typing import Any
from govapp.apps.publisher.models.publish_channels import GeoServerPublishChannel


class Command(base.BaseCommand):
    # Help string
    help = "Perform Geoserver layer healthcheck"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        # Display information
        self.stdout.write("Performing geoserver layer healthcheck...")

        # Go!
        geoserver_publish_channels = GeoServerPublishChannel.objects.filter(active=True, geoserver_pool__enabled=True)
        for geoserver_publish_channel in geoserver_publish_channels:
            geoserver_publish_channel.perform_geoserver_layer_health_check()