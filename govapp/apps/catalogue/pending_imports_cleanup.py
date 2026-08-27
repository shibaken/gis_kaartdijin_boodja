"""Kaartdijin Boodja Catalogue Pending Imports Cleanup."""

# Standard
import logging
import os
import time

# Third-Party
from django import conf

# Local
from govapp.common import local_storage

# Logging
log = logging.getLogger(__name__)


class PendingImportsCleaner:
    """Removes stale, abandoned chunked-upload files from the pending imports staging area."""

    def __init__(self) -> None:
        self.storage = local_storage.LocalStorage()

    def cleanup(self) -> None:
        """Deletes .tmp / .tmp.size files that have not been modified within the stale threshold."""
        pending_import_path = self.storage.get_pending_import_path()
        threshold_days = conf.settings.PENDING_IMPORT_STALE_THRESHOLD_DAYS
        threshold_seconds = threshold_days * 86400
        now = time.time()

        log.info(
            f"Scanning [{pending_import_path}] for stale upload files "
            f"(threshold: {threshold_days} day(s))"
        )

        for filename in os.listdir(pending_import_path):
            if not (filename.endswith('.tmp') or filename.endswith('.tmp.size')):
                continue

            filepath = os.path.join(pending_import_path, filename)

            try:
                age_seconds = now - os.path.getmtime(filepath)
            except OSError as e:
                log.warning(f"Could not stat [{filepath}]: {e}")
                continue

            if age_seconds < threshold_seconds:
                continue

            try:
                os.remove(filepath)
                log.info(
                    f"Deleted stale pending import file: [{filepath}] "
                    f"(age: {age_seconds / 86400:.1f} day(s))"
                )
            except OSError as e:
                log.warning(f"Failed to delete stale pending import file [{filepath}]: {e}")
