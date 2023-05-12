"""Kaartdijin Boodja Catalogue Django Application Cron Jobs."""


# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron


# Logging
log = logging.getLogger(__name__)


# class ScannerCronJob(django_cron.CronJobBase):
#     """Cron Job for the Catalogue Scanner."""
#     schedule = django_cron.Schedule(run_every_mins=conf.settings.CRON_SCANNER_PERIOD_MINS)
#     code = "govapp.catalogue.scanner"

#     def do(self) -> None:
#         """Perform the Scanner Cron Job."""
#         # Log
#         log.info("Scanner cron job triggered, running...")

#         # Run Management Command
#         management.call_command("scan")



class SharepointScannerCronJob(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.CRON_SCANNER_PERIOD_MINS)
    code = "govapp.catalogue.sharepoint_scanner"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("get_sharepoint_files")


class DirectoryScannerCronJob(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.CRON_SCANNER_PERIOD_MINS)
    code = "govapp.catalogue.directory_scanner"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("scan_dir")        