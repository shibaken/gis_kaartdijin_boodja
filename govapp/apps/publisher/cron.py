"""Kaartdijin Boodja Publisher Django Application Cron Jobs."""


# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron

from govapp.apps.publisher.models.publish_channels import GeoServerPublishChannel


# Logging
log = logging.getLogger(__name__)

class PublishGeoServerQueueCronJob(django_cron.CronJobBase):
    """Cron Job for publishing Geoserver queue."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.CRON_SCANNER_PERIOD_MINS)
    code = "govapp.publisher.geoserver_queue"

    def do(self) -> None:
        """Excute items in the geoserver queue."""
        log.info("Publish GeoServerQueue cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_queue")


class GeoServerLayerHealthCheckCronJob(django_cron.CronJobBase):
    schedule = django_cron.Schedule(run_every_mins=conf.settings.GEOSERVER_LAYER_HEALTH_CHECK_PERIOD_MINS)
    code = 'geoserver.publisher.geoserver_layer_health_check_cron_job'

    def do(self):
        log.info("Geoserver layer healthcheck cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_layer_health_check")