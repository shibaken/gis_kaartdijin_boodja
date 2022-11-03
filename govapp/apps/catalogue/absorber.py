"""Kaartdijin Boodja Catalogue Django Application Absorber."""


# Standard
import logging
import pathlib

# Third-Party
from django.db import transaction

# Local
from . import models
from . import readers


# Logging
log = logging.getLogger(__name__)


class Absorber:
    """Absorbs new layers into the system."""

    def absorb(self, filepath: pathlib.Path) -> None:
        """Absorbs new layers into the system.

        Args:
            filepath (pathlib.Path): File to absorb.
        """
        # Determine number of layers in the file
        layers = readers.utils.layers(filepath)

        # Log
        log.info(f"Detected layers: {layers}")

        # Loop through layers
        for layer in layers:
            # Log
            log.info(f"Absorbing layer '{layer}' from '{filepath}'")

            # Absorb layer
            self.absorb_layer(filepath, layer)

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
                file=str(filepath),
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
                file=str(filepath),
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
