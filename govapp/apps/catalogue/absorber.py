"""Kaartdijin Boodja Catalogue Django Application Absorber."""


# Standard
import datetime
import logging
import pathlib

# Third-Party
from django import conf
from django.db import transaction
import reversion

# Local
from . import models
from . import readers
from . import storage

# Typing
from typing import Optional, cast


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

        # Retrieve existing catalogue entry from the database
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.filter(name=metadata.name).first()

        # Check existing catalogue entry
        if not catalogue_entry:
            # Create
            self.create_catalogue_entry(metadata, attributes, symbology, archive)

        else:
            # Update
            self.update_catalogue_entry(catalogue_entry, metadata, attributes, symbology, archive)

    @transaction.atomic
    @reversion.create_revision  # type: ignore[misc]
    def create_catalogue_entry(
        self,
        metadata: readers.types.metadata.Metadata,
        attributes: Optional[list[readers.types.attributes.Attribute]],
        symbology: Optional[readers.types.symbology.Symbology],
        archive: str,
    ) -> None:
        """Creates a new catalogue entry with the supplied values.

        Args:
            metadata (Metadata): Metadata for the entry.
            attributes (Optional[list[Attribute]]): Attributes for the entry.
            symbology (Optional[Symbology]): Symbology for the entry.
            archive (str): Archive URL for the entry
        """
        # Log
        log.info("Creating new catalogue entry")

        # Create Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
            name=metadata.name,
            description=metadata.description,
        )

        # Create Layer Submission
        models.layer_submissions.LayerSubmission.objects.create(
            name=metadata.name,
            description=metadata.description,
            file=archive,
            is_active=True,  # Active!
            catalogue_entry=catalogue_entry,
        )

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

    @transaction.atomic
    @reversion.create_revision  # type: ignore[misc]
    def update_catalogue_entry(
        self,
        catalogue_entry: models.catalogue_entries.CatalogueEntry,
        metadata: readers.types.metadata.Metadata,
        attributes: Optional[list[readers.types.attributes.Attribute]],
        symbology: Optional[readers.types.symbology.Symbology],
        archive: str,
    ) -> None:
        """Creates a new catalogue entry with the supplied values.

        Args:
            catalogue_entry (CatalogueEntry): Catalogue entry to update.
            metadata (Metadata): Metadata for the entry.
            attributes (Optional[list[Attribute]]): Attributes for the entry.
            symbology (Optional[Symbology]): Symbology for the entry.
            archive (str): Archive URL for the entry
        """
        # Log
        log.info("Updating existing catalogue entry")

        # Check the created date?
        # TODO
        ...

        # Retrieve the Catalogue Entry attributes for comparison
        # We also cast the type here to help `mypy` with the Django backwards relation
        current_attributes = list(catalogue_entry.attributes.all())
        current_attributes = cast(list[models.layer_attributes.LayerAttribute], current_attributes)

        # Compare Attributes
        attributes_match = self.compare_attributes(current_attributes, attributes)

        # Check if they match!
        if attributes_match:
            # Log
            log.info("Attributes match, updating catalogue entry")

            # Retrieve Current Active Layer
            current_active_layer = catalogue_entry.active_layer

            # Determine behaviour bases on current status
            if catalogue_entry.is_new():
                # Catalogue Entry is new
                # Set the new incoming layer submission to SUBMITTED
                # Set the old active layer to DECLINED
                new_status = models.layer_submissions.LayerSubmissionStatus.SUBMITTED
                current_active_layer.status = models.layer_submissions.LayerSubmissionStatus.DECLINED

            else:
                # Set the new incoming layer submission to ACCEPTED
                new_status = models.layer_submissions.LayerSubmissionStatus.ACCEPTED

            # Update!
            # Update Catalogue Entry Current Active Layer to Inactive
            # Create New Active Layer Submission with Status ACCEPTED
            current_active_layer.is_active = False
            current_active_layer.save()
            models.layer_submissions.LayerSubmission.objects.create(
                name=metadata.name,
                description=metadata.description,
                file=archive,
                is_active=True,  # Active Layer!
                status=new_status,
                catalogue_entry=catalogue_entry,
            )

        else:
            # Log
            log.info("Attributes do not match, layer submission failed")

            # Failure!
            # Do not update Catalogue Entry
            # Create New Inactive Layer Submission with Status DECLINED
            models.layer_submissions.LayerSubmission.objects.create(
                name=metadata.name,
                description=metadata.description,
                file=archive,
                is_active=False,
                status=models.layer_submissions.LayerSubmissionStatus.DECLINED,
                catalogue_entry=catalogue_entry,
            )

    def compare_attributes(
        self,
        current_attributes: Optional[list[models.layer_attributes.LayerAttribute]],
        new_attributes: Optional[list[readers.types.attributes.Attribute]],
    ) -> bool:
        """Compares existing current attributes with new attributes.

        Args:
            current_attributes (Optional[list[LayerAttribute]]): Current attributes
            new_attributes (Optional[list[Attribute]]): New attributes

        Returns:
            bool: Whether the attributes match
        """
        # Check that attributes exist
        # Replace with an empty list if they are None so the comparison is easier
        new_attributes = [] if not new_attributes else new_attributes
        current_attributes = [] if not current_attributes else current_attributes

        # Compare the number of attributes
        if not len(current_attributes) == len(new_attributes):
            # They can't match!
            return False

        # First, sort the attributes by their "order"
        # This is just in case the order of the lists is not determinstic
        current_attributes = sorted(current_attributes, key=lambda x: x.order)
        new_attributes = sorted(new_attributes, key=lambda x: x.order)

        # Compare the attributes
        for (current, new) in zip(current_attributes, new_attributes):
            # Compare
            if (current.name, current.type, current.order) != (new.name, new.type, new.order):
                # They can't match!
                return False

        # They match!
        return True
