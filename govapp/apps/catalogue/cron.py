"""Kaartdijin Boodja Catalogue Django Application Cron Jobs."""


# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron


# Logging
log = logging.getLogger(__name__)


class PostgresScannerCronJob(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.POSTGRES_SCANNER_PERIOD_MINS)
    code = "govapp.catalogue.postgres_scanner"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Postgres Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("scan_postgres")

class SharepointScannerCronJob(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.SHAREPOINT_SCANNER_PERIOD_MINS)
    code = "govapp.catalogue.sharepoint_scanner"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Sharepoint Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("get_sharepoint_files")


class DirectoryScannerCronJob(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.DIRECTORY_SCANNER_PERIOD_MINS)
    code = "govapp.catalogue.directory_scanner"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Directory Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("scan_dir")        


class PendingImportsCleanupCronJob(django_cron.CronJobBase):
    """Cron Job to remove stale, abandoned chunked-upload files from pending imports."""
    schedule = django_cron.Schedule(run_every_mins=conf.settings.PENDING_IMPORTS_CLEANUP_PERIOD_MINS)
    code = "govapp.catalogue.cleanup_pending_imports"

    def do(self) -> None:
        """Perform the Cleanup Pending Imports Cron Job."""
        # Log
        log.info("Cleanup Pending Imports cron job triggered, running...")

        # Run Management Command
        management.call_command("cleanup_pending_imports")