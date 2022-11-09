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

        # Retrieve File
        filepath = self.storage.get(path)

        # Log
        log.info(f"Retrieved '{path}' -> '{filepath}'")

        # Determine the layers in the file
        layers = readers.utils.layers(filepath)

        # Log
        log.info(f"Detected layers: {layers}")

        # Loop through layers
        for layer in layers:
            # Log
            log.info(f"Absorbing layer '{layer}' from '{filepath}'")

            # Absorb layer
            self.absorb_layer(filepath, layer)

        # Delete Files
        self.storage.delete(path)
        filepath.unlink()

    def absorb_layer(self, filepath: pathlib.Path, layer: str) -> None:
        """Absorbs a layer into the system.

        Args:
            filepath (pathlib.Path): File to absorb layer from.
            layer (str): Layer to absorb.
        """
        # Log
        log.info(f"Extracting data from layer: '{layer}'")

        # Extract attributes, metadata and symbology
        attributes = readers.utils.attributes(filepath, layer)
        metadata = readers.utils.metadata(filepath, layer)
        symbology = readers.utils.symbology(filepath, layer)

        # Create Archived GIS File and Symbology
        archive = f"{conf.settings.SHAREPOINT_ARCHIVE_AREA}/{datetime.date.today().year}"
        gpkg = self.storage.put(f"{archive}/{metadata.name}.gpkg", filepath.read_bytes())
        sld = self.storage.put(f"{archive}/{metadata.name}.xml", symbology.sld.encode("UTF-8"))

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
                file=gpkg,
                catalogue_entry=catalogue_entry,
            )

            # Update Catalogue Entry Active Layer
            catalogue_entry.active_layer = layer_submission
            catalogue_entry.save()

            # Create Layer Metadata
            models.layer_metadata.LayerMetadata.objects.create(
                name=metadata.name,
                created_at=metadata.created_at,
                layer=layer_submission
            )

            # Create Layer Symbology
            models.layer_symbology.LayerSymbology.objects.create(
                name=symbology.name,
                file=sld,
                layer=layer_submission,
            )

            # Loop through attributes
            for attribute in attributes:
                # Create Attribute
                models.layer_attributes.LayerAttribute.objects.create(
                    name=attribute.name,
                    type=attribute.type,
                    order=attribute.order,
                    layer=layer_submission,
                )
