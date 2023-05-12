"""Kaartdijin Boodja Catalogue Django Application Absorber."""


# Standard
import datetime
import logging
import pathlib
import shutil

# Third-Party
from django import conf
from django.db import transaction

# Local
from govapp.common import sharepoint
from govapp.gis import readers
from govapp.apps.catalogue import models
from govapp.apps.catalogue import notifications
from govapp.apps.catalogue import utils


# Logging
log = logging.getLogger(__name__)


class Absorber:
    """Absorbs new layers into the system."""

    def __init__(self) -> None:
        """Instantiates the Absorber."""
        # Storage
        self.storage = sharepoint.sharepoint_input()

    def absorb(self, path: str) -> None:
        """Absorbs new layers into the system.

        Args:
            path (str): File to absorb.
        """
        # Log
        log.info(f"Retrieving '{path}' from storage")

        # Retrieve file from remote storage
        # This retrieves and writes the file to our own temporary filesystem
        filepath = self.storage.get(path)

        # Move the file on the remote storage into the archive area
        # The file is renamed to include a UTC timestamp, to avoid collisions
        timestamp = datetime.datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
        archive_directory = f"{conf.settings.SHAREPOINT_INPUT_ARCHIVE_AREA}/{timestamp.year}"
        archive_path = f"{archive_directory}/{filepath.stem}.{timestamp_str}{filepath.suffix}"
        archive = self.storage.put(archive_path, filepath.read_bytes())  # Move file to archive
        self.storage.delete(path)  # Delete file in staging area

        # Log
        log.info(f"Retrieved '{path}' -> '{filepath}'")
        log.info(f"Archived '{path}' -> {archive_path} ({archive})")

        # Copy sharepoint files to a local storage
        ## Write code to move share point files with ENV in settings



    