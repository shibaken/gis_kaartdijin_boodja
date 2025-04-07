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
    schedule = django_cron.Schedule(run_every_mins=conf.settings.PUBLISH_GEOSERVER_QUEUE_PERIOD_MINS)
    code = "govapp.publisher.geoserver_execute_queue"

    def do(self) -> None:
        """Excute items in the geoserver queue."""
        log.info("Publish GeoServerQueue cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_execute_queue")


class GeoServerLayerHealthcheckCronJob(django_cron.CronJobBase):
    schedule = django_cron.Schedule(run_every_mins=conf.settings.GEOSERVER_LAYER_HEALTH_CHECK_PERIOD_MINS)
    code = 'geoserver.publisher.geoserver_layer_health_check_cron_job'

    def do(self):
        log.info("Geoserver layer healthcheck cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_layer_health_check")


class GeoServerSyncLayersCronJob(django_cron.CronJobBase):  # layers
    schedule = django_cron.Schedule(run_every_mins=conf.settings.GEOSERVER_SYNC_LAYERS_PERIOD_MINS)
    code = 'geoserver.publisher.geoserver_sync_layers_cron_job'

    def do(self):
        log.info("Sync geoserver layers cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_sync_layers")


class GeoServerSyncRulesCronJob(django_cron.CronJobBase):  # rules
    schedule = django_cron.Schedule(run_every_mins=conf.settings.GEOSERVER_SYNC_RULES_PERIOD_MINS)
    code = 'geoserver.publisher.geoserver_sync_rules_cron_job'

    def do(self):
        log.info("Sync geoserver rules cron job triggered, running...")

        # Run Management Command
        management.call_command("geoserver_sync_rules")