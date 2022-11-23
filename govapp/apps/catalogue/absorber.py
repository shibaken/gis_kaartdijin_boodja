"""Kaartdijin Boodja Catalogue Django Application Absorber."""


# Standard
import datetime
import logging
import pathlib

# Third-Party
from django import conf
from django.db import transaction

# Local
from . import models
from . import readers
from . import storage


# Logging
log = logging.getLogger(__name__)


class Absorber:
    """Absorbs new layers into the system."""

    def __init__(self) -> None:
        """Instantiates the Absorber."""
        # Storage
        self.storage = storage.sharepoint.SharepointStorage(
            url=conf.settings.SHAREPOINT_URL,
            root=conf.settings.SHAREPOINT_LIST,
            username=conf.settings.SHAREPOINT_USERNAME,
            password=conf.settings.SHAREPOINT_PASSWORD,
        )

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
        archive_directory = f"{conf.settings.SHAREPOINT_ARCHIVE_AREA}/{timestamp.year}"
        archive_path = f"{archive_directory}/{filepath.stem}.{timestamp_str}{filepath.suffix}"
        archive = self.storage.put(archive_path, filepath.read_bytes())  # Move file to archive
        self.storage.delete(path)  # Delete file in staging area

        # Log
        log.info(f"Retrieved '{path}' -> '{filepath}'")
        log.info(f"Archived '{path}' -> {archive_path} ({archive})")

        # Determine the layers in the file
        layers = readers.utils.layers(filepath)

        # Log
        log.info(f"Detected layers: {layers}")

        # Loop through layers
        for layer in layers:
            # Log
            log.info(f"Absorbing layer '{layer}' from '{filepath}'")

            # Absorb layer
            self.absorb_layer(filepath, layer, archive)

        # Delete local temporary copy of file
        filepath.unlink()

    def absorb_layer(self, filepath: pathlib.Path, layer: str, archive: str) -> None:
        """Absorbs a layer into the system.

        Args:
            filepath (pathlib.Path): File to absorb layer from.
            layer (str): Layer to absorb.
            archive (str): URL to the archived file for this layer.
        """
        # Log
        log.info(f"Extracting data from layer: '{layer}'")

        # Extract metadata
        metadata = readers.utils.metadata(filepath, layer)

        # Attempt to extract attributes
        try:
            # Extract attributes
            attributes = readers.utils.attributes(filepath, layer)

        except ValueError:
            # Could not extract attributes
            attributes = None

        # Attempt to extract symbology
        try:
            # Extract symbology
            symbology = readers.utils.symbology(filepath, layer)

        except ValueError:
            # Could not extract symbology
            symbology = None

        # Enter Atomic Database Transaction
        with transaction.atomic():
            # Create Catalogue Entry
            catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
                name=metadata.name,
                description=metadata.description,
            )

            # Create Layer Submission
            layer_submission = models.layer_submissions.LayerSubmission.objects.create(
                name=metadata.name,
                description=metadata.description,
                file=archive,
                catalogue_entry=catalogue_entry,
            )

            # Update Catalogue Entry Active Layer
            catalogue_entry.active_layer = layer_submission
            catalogue_entry.save()

            # Create Layer Metadata
            models.layer_metadata.LayerMetadata.objects.create(
                name=metadata.name,
                created_at=metadata.created_at,
                catalogue_entry=catalogue_entry,
            )

            # Check symbology
            if symbology:
                # Create Layer Symbology
                models.layer_symbology.LayerSymbology.objects.create(
                    name=symbology.name,
                    sld=symbology.sld,
                    catalogue_entry=catalogue_entry,
                )

            # Check attributes
            if attributes:
                # Loop through attributes
                for attribute in attributes:
                    # Create Attribute
                    models.layer_attributes.LayerAttribute.objects.create(
                        name=attribute.name,
                        type=attribute.type,
                        order=attribute.order,
                        catalogue_entry=catalogue_entry,
                    )
