"""Kaartdijin Boodja Catalogue Django Application Absorber."""

# Standard
import datetime
import logging
import pathlib
import shutil
import os
import tempfile
from typing import Optional
import uuid
import zipfile

# Third-Party
from django import conf
from django.db import transaction
import py7zr
import pytz
import osgeo

# Local
from govapp.common import local_storage
from govapp.gis import readers
from govapp.gis.conversions import to_geojson
from govapp.apps.catalogue import models
from govapp.apps.catalogue import directory_notifications
from govapp.apps.catalogue import utils
from govapp.gis.readers import types


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
        log.info(f"Retrieving '[{path}]' from storage...")        

        # # Retrieve file from remote storage
        # # This retrieves and writes the file to our own temporary filesystem
        filepath = self.storage.get_path(path)        
        filepath = pathlib.Path(filepath)
        # Move the file on the remote storage into the archive area
        # The file is renamed to include a UTC timestamp, to avoid collisions
        timestamp = datetime.datetime.now(pytz.utc)
        timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
        storage_directory = os.path.join(self.storage.get_data_storage_path(), f'{timestamp.year}')
        if not os.path.exists(storage_directory):
            os.makedirs(storage_directory)
            log.info(f"Directory created: [{storage_directory}]")

        storage_path = os.path.join(storage_directory, filepath.stem + "." + timestamp_str + filepath.suffix)
        archive = self.storage.move_to_storage(filepath, storage_path)  # Move file to archive

        # # Log
        log.info(f"Retrieved '{path}' -> '{filepath}'")
        log.info(f"Archived '{path}' -> {storage_path} ({archive})")

        self.process_file(storage_path)
        
    def process_file(self, path_to_file):
        """
        Extracts .7z or .zip files to a temp folder and executes get_gis_layers_from_file() on each extracted file.
        For .tiff or .tif files, executes get_gis_layers_from_file() directly.
        """
        # Get the directory containing the archive file
        folder_path = os.path.dirname(path_to_file)
        
        # Create a folder with the same name as the archive file (without extension)
        folder_name = os.path.splitext(os.path.basename(path_to_file))[0]
        temp_dir = os.path.join(folder_path, folder_name)

        try:
            filepaths_to_process = []
            file_ext = os.path.splitext(path_to_file)[1].lower()
            if file_ext in ['.7z', '.zip',]:
                os.makedirs(temp_dir, exist_ok=True)
                if file_ext == '.7z':
                    # Extract .7z file
                    with py7zr.SevenZipFile(path_to_file, mode='r') as z:
                        z.extractall(path=temp_dir)
                elif file_ext == '.zip':
                    # Extract .zip file
                    with zipfile.ZipFile(path_to_file, 'r') as z:
                        z.extractall(path=temp_dir)

                # If extracted, loop through extracted files and process them
                for extracted_filepath in os.listdir(temp_dir):
                    filepaths_to_process.append(os.path.join(temp_dir, extracted_filepath))
                
            else:
                filepaths_to_process.append(path_to_file)

            # Process all the files
            for filepath in filepaths_to_process:
                if filepath.lower().endswith(('.tiff', '.tif')):
                    # Call a different function if the file is a TIFF
                    self.process_tiff_file(filepath)
                else:
                    # Call the original function for other file types
                    self.process_vector_file(filepath)
            
        finally:
            pass
        #     if os.path.exists(temp_dir):
        #         # Clean up temp directory
        #         shutil.rmtree(temp_dir)
        #         log.info(f'Remove the directory: [{temp_dir}]')

    def process_tiff_file(self, filepath):
        # Convert the file path to a pathlib.Path object
        pathlib_filepath = pathlib.Path(filepath)
        
        result = {'total': 1, 'success':[], 'fail':[]}
        # Create CatalogueEntry
        try:
            self.absorb_tiff_as_layer(pathlib_filepath)
            result['success'].append(pathlib_filepath.name)
        except Exception as exc:
            result['fail'].append(f"layer:{pathlib_filepath.name}, exception:{exc}")
            # Log and continue
            log.error(f"Error absorbing tiff as a layer:'{pathlib_filepath.name}': file:'{filepath}'", exc_info=exc)

        log.info(f"End of absorbing layers from '{filepath}' :  fail:{len(result['fail'])} success:{len(result['success'])} total:{result['total']}")
        log.info(f" - Succeed layers : {result['success']}\n - Failed layers : {result['fail']}")

    def absorb_tiff_as_layer(self, pathlib_filepath):
        # Open the file with GDAL
        dataset = osgeo.gdal.Open(str(pathlib_filepath))
        if dataset is None:
            log.error(f'Failed to open file: {str(pathlib_filepath)}')
            return
        additional_data = utils.retrieve_additional_data(dataset)
        
        metadata = types.Metadata(
            name=utils.get_first_part_of_filename(pathlib_filepath),  # filename is like: State_Map_Base_FMS.20240606T015418.tif
            description="",  # Blank by Default
            created_at=datetime.datetime.now(datetime.timezone.utc),
            additional_data=additional_data,
        )

        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.filter(name=metadata.name).first()

        # Check existing catalogue entry
        if not catalogue_entry:
            self.create_catalogue_entry(metadata, str(pathlib_filepath))
        else:
            self.update_catalogue_entry(catalogue_entry, metadata, str(pathlib_filepath))
        
        # Clean up GDAL dataset
        dataset = None

    def process_vector_file(self, filepath):
        pathlib_filepath = pathlib.Path(filepath)
        # # Construct Reader
        reader = readers.reader.FileReader(pathlib_filepath)

        result = {'total':reader.layer_count(), 'success':[], 'fail':[]}
        # Create catalogue entries by looping through the layers
        for layer in reader.layers():
            log.info(f"Absorbing layer '{layer.name}' from '{filepath}'")

            try:
                # Absorb layer
                self.absorb_vector_layer(layer, filepath)
                result['success'].append(layer.name)
            except Exception as exc:
                result['fail'].append(f"layer:{layer.name}, exception:{exc}")
                # Log and continue
                log.error(f"Error absorbing layer:'{layer.name}': file:'{filepath}'", exc_info=exc)

            log.info(f"Processing.. fail:{len(result['fail'])} success:{len(result['success'])} total:{result['total']}")

        log.info(f"End of absorbing layers from '{filepath}' :  fail:{len(result['fail'])} success:{len(result['success'])} total:{result['total']}")
        log.info(f" - Succeed layers : {result['success']}\n - Failed layers : {result['fail']}")

    def absorb_vector_layer(self, layer: readers.base.LayerReader, archive: str) -> None:
        """Absorbs a layer into the system.

        Args:
            layer (readers.base.LayerReader): Layer to absorb.
            archive (str): URL to the archived file for this layer.
        """
        # Log
        log.info(f"Extracting data from layer: '{layer.name}'")

        # Extract metadata, attributes and symbology
        metadata = layer.metadata()
        attributes = layer.attributes()
        symbology = layer.symbology()

        log.info(f"Extracting data from layer: '{attributes}'")
        # Retrieve existing catalogue entry from the database
        # Here we specifically check the Layer Metadata name
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.filter(name=metadata.name).first()

        # Check existing catalogue entry
        if not catalogue_entry:
            # Create
            self.create_catalogue_entry(metadata, archive, attributes, symbology)
        else:
            # Update
            self.update_catalogue_entry(catalogue_entry, metadata, archive, attributes, symbology)

    @transaction.atomic()
    def create_catalogue_entry(
        self,
        metadata: readers.types.Metadata,
        archive: str,
        attributes: Optional[list[readers.types.Attribute]] = [],
        symbology: Optional[readers.types.Symbology] = None,
    ) -> bool:
        """Creates a new catalogue entry with the supplied values.

        Args:
            metadata (Metadata): Metadata for the entry.
            archive (str): Archive URL for the entry
            attributes (list[Attribute]): Attributes for the entry.
            symbology (Symbology): Symbology for the entry.

        Returns:
            bool: Whether the creation was successful.
        """
        # Log
        log.info(f"Creating a new CatalogueEntry with the name: [{metadata.name}]...")
        
        # Calculate attributes hash
        attributes_hash = utils.attributes_hash(attributes)

        attributes_str = ""
        for attr in attributes:
            attributes_str = attributes_str+str(attr)+"\n"

        # Create Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
            name=metadata.name,
            description=metadata.description,
        )
        log.info(f'New CatalogueEntry: [{catalogue_entry}] has been created.')

        # Convert to a Geojson text
        extension = pathlib.Path(archive).suffix.lower()
        geojson_path = '' if extension in ['.tif', '.tiff'] else self.convert_to_geojson(archive, catalogue_entry)

        # Create Layer Submission
        self.create_layer_submission(metadata, archive, attributes_hash, attributes_str, catalogue_entry, geojson_path)

        # Create Layer Metadata
        self.create_layer_metadata(metadata, catalogue_entry)

        # Loop through attributes
        if attributes:
            self.create_layer_attributes(attributes, catalogue_entry)

        # Create Layer Symbology
        if symbology:
            self.create_layer_symbology(symbology, catalogue_entry)

        # Notify!
        directory_notifications.catalogue_entry_creation(catalogue_entry)

        # Return
        return True

    def create_layer_submission(self, metadata, archive, attributes_hash, attributes_str, catalogue_entry, geojson_path):
        models.layer_submissions.LayerSubmission.objects.create(
            description=metadata.description,
            file=archive,
            is_active=True,  # Active!
            created_at=metadata.created_at,
            hash=attributes_hash,
            layer_attribute=attributes_str,
            catalogue_entry=catalogue_entry,
            geojson=geojson_path
        )

    def create_layer_metadata(self, metadata, catalogue_entry):
        models.layer_metadata.LayerMetadata.objects.create(
            created_at=metadata.created_at,
            catalogue_entry=catalogue_entry,
            additional_data=metadata.additional_data,
        )

    def create_layer_attributes(self, attributes, catalogue_entry):
        for attribute in attributes:
            # Create Attribute
            models.layer_attributes.LayerAttribute.objects.create(
                name=attribute.name,
                type=attribute.type,
                order=attribute.order,
                catalogue_entry=catalogue_entry,
            )

    def create_layer_symbology(self, symbology, catalogue_entry):
        models.layer_symbology.LayerSymbology.objects.create(
            sld=symbology.sld,
            catalogue_entry=catalogue_entry,
        )

    @transaction.atomic()
    def update_catalogue_entry(
        self,
        catalogue_entry: models.catalogue_entries.CatalogueEntry,
        metadata: readers.types.Metadata,
        archive: str,
        attributes: Optional[list[readers.types.Attribute]] = [],
        symbology: Optional[readers.types.Symbology] = None,
    ) -> bool:
        """Update a existing catalogue entry with the supplied values.

        Args:
            catalogue_entry (CatalogueEntry): Catalogue entry to update.
            metadata (Metadata): Metadata for the entry.
            archive (str): Archive URL for the entry.
            attributes (list[Attribute]): Attributes for the entry.
            symbology (Symbology): Symbology for the entry.

        Returns:
            bool: Whether the update was successful.
        """
        # Log
        log.info("Updating existing catalogue entry")
        
        # Calculate Layer Submission Attributes Hash
        attributes_hash = utils.attributes_hash(attributes)
        
        attributes_str = ""
        for attr in attributes:
            attributes_str = attributes_str+str(attr)+"\n"

        # Convert to a Geojson text
        geojson_path = self.convert_to_geojson(archive, catalogue_entry)

        # Create New Layer Submission
        layer_submission = models.layer_submissions.LayerSubmission.objects.create(
            description=metadata.description,
            file=archive,
            is_active=False,  # Starts out Inactive
            created_at=metadata.created_at,
            hash=attributes_hash,
            layer_attribute=attributes_str,
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

