"""Kaartdijin Boodja Catalogue Django Application Scanner."""


# Standard
import logging

# Third-Party
from django import conf

# Local
from govapp.common import sharepoint
from govapp.apps.catalogue import sharepoint_absorber
from govapp.apps.catalogue import notifications


# Logging
log = logging.getLogger(__name__)


class Scanner:
    """Scans for files to be absorbed into the system."""

    def __init__(self) -> None:
        """Instantiates the Scanner."""
        # Storage
        self.storage = sharepoint.sharepoint_input()

    def scan(self) -> None:
        """Scans for new files in the staging area to be absorbed."""
        # Log
        log.info("Scanning storage staging area for files to absorb")

        # Retrieve file from remote storage staging area
        files = self.storage.list(conf.settings.SHAREPOINT_INPUT_STAGING_AREA)

        # Check for files
        if not files:
            # Log
            log.info("No files found")

        # Loop through files
        for file in files:
            # Log
            log.info(f"Discovered file '{file}'")

            # Handle errors
            # For example, if someone drops in a malformed file or a non-GIS file
            try:
                # Absorb!
                sharepoint_absorber.Absorber().absorb(file)

            except Exception as exc:
                # Log and continue
                log.error(f"Error absorbing file '{file}': {exc}")

                # Notify!
                notifications.file_absorb_failure(file)

        # Log
        log.info("Scanning storage staging area complete!")
