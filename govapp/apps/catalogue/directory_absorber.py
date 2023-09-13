"""Kaartdijin Boodja Catalogue Django Application Absorber."""

# Standard
import datetime
import logging
import pathlib
import shutil
import os
import uuid

# Third-Party
from django import conf
from django.db import transaction

# Local
from govapp.common import local_storage
from govapp.gis import readers
from govapp.gis.conversions import to_geojson
from govapp.apps.catalogue import models
from govapp.apps.catalogue import directory_notifications
from govapp.apps.catalogue import utils


# Logging
log = logging.getLogger(__name__)


class Absorber:
    """Absorbs new layers into the system."""

    def __init__(self) -> None:
        """Instantiates the Absorber."""
        # Storage
        self.storage = local_storage.LocalStorage()

    def absorb(self, path: str) -> None:
        """Absorbs new layers into the system.

        Args:
            path (str): File to absorb.
        """
        # Log
        log.info(f"Retrieving '{path}' from storage")        

        # # Retrieve file from remote storage
        # # This retrieves and writes the file to our own temporary filesystem
        filepath = self.storage.get_path(path)        
        filepath = pathlib.Path(filepath)
        # Move the file on the remote storage into the archive area
        # The file is renamed to include a UTC timestamp, to avoid collisions
        timestamp = datetime.datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
        storage_directory = f"{self.storage.get_data_storage_path()}/{timestamp.year}/"
        if not os.path.exists(storage_directory):
            print ("creating directory")
            print (storage_directory)
            os.makedirs(storage_directory)

        storage_path = f"{storage_directory}{filepath.stem}.{timestamp_str}{self.storage.get_path_suffix(path)}"
        archive = self.storage.move_to_storage(filepath, storage_path)  # Move file to archive
        # self.storage.delete(path)  # Delete file in staging area

        # # Log
        log.info(f"Retrieved '{path}' -> '{filepath}'")
        log.info(f"Archived '{path}' -> {storage_path} ({archive})")

        pathlib_storage_path = pathlib.Path(storage_path)
        # # Construct Reader
        reader = readers.reader.FileReader(pathlib_storage_path)

        result = {'total':reader.layer_count(), 'success':[], 'fail':[]}
        # Loop through layers
        for layer in reader.layers():
            # Log
            log.info(f"Absorbing layer '{layer.name}' from '{storage_path}'")
            try:
                # Absorb layer
                self.absorb_layer(pathlib_storage_path, layer, storage_path)
                result['success'].append(layer.name)
            except Exception as exc:
                result['fail'].append(f"layer:{layer.name}, exception:{exc}")
                # Log and continue
                log.error(f"Error absorbing layer:'{layer.name}': file:'{filepath.name}'", exc_info=exc)
            log.info(f"Processing.. fail:{len(result['fail'])} success:{len(result['success'])} totla:{result['total']}")
        log.info(f"End of absorbing layers from '{storage_path}' :  fail:{len(result['fail'])} success:{len(result['success'])} totla:{result['total']}")
        log.info(f" - Succeed layers : {result['success']}\n - Failed layers : {result['fail']}")

        # Delete local temporary copy of file if we can
        # shutil.rmtree(storage_directory, ignore_errors=True)

    def absorb_layer(self, filepath: pathlib.Path, layer: readers.base.LayerReader, archive: str) -> None:
        """Absorbs a layer into the system.

        Args:
            filepath (pathlib.Path): File to absorb layer from.
            layer (readers.base.LayerReader): Layer to absorb.
            archive (str): URL to the archived file for this layer.
        """
        # Log
        log.info(f"Extracting data from layer: '{layer.name}'")

        # Extract metadata, attributes and symbology
        metadata = layer.metadata()
        attributes = layer.attributes()
        symbology = layer.symbology()
        import json
        log.info(f"Extracting data from layer: '{attributes}'")
        # Retrieve existing catalogue entry from the database
        # Here we specifically check the Layer Metadata name
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.filter(name=metadata.name).first()

        # Check existing catalogue entry
        if not catalogue_entry:
            # Create
            self.create_catalogue_entry(metadata, attributes, symbology, archive)

        else:
            # Update
            self.update_catalogue_entry(catalogue_entry, metadata, attributes, symbology, archive)

    @transaction.atomic()
    def create_catalogue_entry(
        self,
        metadata: readers.types.Metadata,
        attributes: list[readers.types.Attribute],
        symbology: readers.types.Symbology,
        archive: str,
    ) -> bool:
        """Creates a new catalogue entry with the supplied values.

        Args:
            metadata (Metadata): Metadata for the entry.
            attributes (list[Attribute]): Attributes for the entry.
            symbology (Symbology): Symbology for the entry.
            archive (str): Archive URL for the entry

        Returns:
            bool: Whether the creation was successful.
        """
        # Log
        log.info("Creating new catalogue entry")
        
        # Calculate attributes hash
        attributes_hash = utils.attributes_hash(attributes)

        # Create Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
            name=metadata.name,
            description=metadata.description,
        )

        # Convert to a Geojson text
        geojson_path = self.convert_to_geojson(archive, catalogue_entry)

        # Create Layer Submission
        models.layer_submissions.LayerSubmission.objects.create(
            description=metadata.description,
            file=archive,
            is_active=True,  # Active!
            created_at=metadata.created_at,
            hash=attributes_hash,
            catalogue_entry=catalogue_entry,
            geojson=geojson_path
        )

        # Create Layer Metadata
        models.layer_metadata.LayerMetadata.objects.create(
            created_at=metadata.created_at,
            catalogue_entry=catalogue_entry,
        )

        # Loop through attributes
        for attribute in attributes:
            # Create Attribute
            models.layer_attributes.LayerAttribute.objects.create(
                name=attribute.name,
                type=attribute.type,
                order=attribute.order,
                catalogue_entry=catalogue_entry,
            )

        # Create Layer Symbology
        models.layer_symbology.LayerSymbology.objects.create(
            sld=symbology.sld,
            catalogue_entry=catalogue_entry,
        )

        # Notify!
        directory_notifications.catalogue_entry_creation(catalogue_entry)

        # Return
        return True

    @transaction.atomic()
    def update_catalogue_entry(
        self,
        catalogue_entry: models.catalogue_entries.CatalogueEntry,
        metadata: readers.types.Metadata,
        attributes: list[readers.types.Attribute],
        symbology: readers.types.Symbology,
        archive: str,
    ) -> bool:
        """Update a existing catalogue entry with the supplied values.

        Args:
            catalogue_entry (CatalogueEntry): Catalogue entry to update.
            metadata (Metadata): Metadata for the entry.
            attributes (list[Attribute]): Attributes for the entry.
            symbology (Symbology): Symbology for the entry.
            archive (str): Archive URL for the entry.

        Returns:
            bool: Whether the update was successful.
        """
        # Log
        log.info("Updating existing catalogue entry")
        
        # Calculate Layer Submission Attributes Hash
        attributes_hash = utils.attributes_hash(attributes)
        
        # Convert to a Geojson text
        geojson_path = self.convert_to_geojson(archive, catalogue_entry)

        # Create New Layer Submission
        layer_submission = models.layer_submissions.LayerSubmission.objects.create(
            description=metadata.description,
            file=archive,
            is_active=False,  # Starts out Inactive
            created_at=metadata.created_at,
            hash=attributes_hash,
            catalogue_entry=catalogue_entry,
            geojson=geojson_path
        )    
        
        # Attempt to "Activate" this Layer Submission
        layer_submission.activate(False)
        
        # Check Success
        success = not layer_submission.is_declined()
        
        # Check Layer Submission
        if success:
            # Check for Publish Entry
            if hasattr(catalogue_entry, "publish_entry"):                
                # Publish
                catalogue_entry.publish_entry.publish()  # type: ignore[union-attr]

            # Notify!
            directory_notifications.catalogue_entry_update_success(catalogue_entry)

        else:
            # Send Update Failure Email
            directory_notifications.catalogue_entry_update_failure(catalogue_entry)
        # Return
        return success

    def convert_to_geojson(
        self, 
        filepath: str, 
        catalogue_entry: models.catalogue_entries.CatalogueEntry) -> pathlib.Path:
        # Convert to a Geojson file
        path_from = to_geojson(
            filepath=pathlib.Path(filepath),
            layer=catalogue_entry.name,
            catalogue_name=catalogue_entry.name,
            export_method=None
        )
        return self.move_file_to_storage_with_uniquename(path_from)

    def move_file_to_storage_with_uniquename(self, path_from:pathlib.Path):
        # Create a new folder hierarchically named to today's date(./yyyy/mm/dd) in the data storage when it dosen't exist
        # date_str = datetime.date.today().strftime("%d%m%Y")
        data_storage_path = f"{self.storage.get_data_storage_path()}/geojson/{datetime.date.today().year}/{str(datetime.date.today().month).zfill(2)}/{datetime.date.today().day}"
        if not os.path.exists(data_storage_path):
            os.makedirs(data_storage_path)
        
        # Change the file name with uuid and join with the data storage path
        filename_to = f"{path_from.stem}_{str(uuid.uuid4())}{path_from.suffix}"
        path_to = f"{data_storage_path}/{filename_to}"

        # Move the file into a folder named date(ddmmyyyy) in the data storage
        if self.storage.move_to_storage(str(path_from), path_to):
            return path_to
        
        # Raise Exception when it failed for some reasons
        raise Exception(f"failed to move file from {path_from} to {path_to}")

