"""Base class for reading GIS files."""


# Standard
import logging
import pathlib

# Third-Party
from osgeo import ogr, gdal

# Local
from govapp.gis import compression
from govapp.gis import utils
from govapp.gis.readers import base

# Typing
from typing import Iterable

from govapp.gis.readers.formats.geojson import GeoJSONReader


# Logging
logger = logging.getLogger(__name__)


class FileReader:
    """Reader Protocol."""

    def __init__(self, file: pathlib.Path) -> None:
        """Instantiates the GIS File Reader.

        Args:
            file (pathlib.Path): Filepath to read.
        """
        # Store filepath
        # Decompress and Flatten if Required
        self.file = file
        self.file = compression.decompress(self.file)  # Extracted foler path is returned when the file is a compressed file, otherwise the original file path is returned
        self.file = compression.flatten(self.file)  # Returns the path to the innermost single subdirectory if only one subdirectory exists at each level, otherwise it returns the original path.

        # Get layer reader class
        self.reader = utils.get_reader(self.file)

        if self.reader == GeoJSONReader:
            logger.info(f'self.reader is GeoJSONReader class')
            geojson_files = self.reader.get_geojson_files(self.file)
            logger.info(f'files: {geojson_files}')
            if len(geojson_files) == 1:
                # Load data source
                value = ogr.Open(str(geojson_files[0]))
            else:
                logger.error(f'There are more than one GeoJSON files in the folder: [{self.file}]')
                raise ValueError(f'There are more than one GeoJSON files in the folder: [{self.file}]')
        else:
            # Load data source
            value = ogr.Open(str(self.file))  # !!! This function is able to accept a path to a folder as a parameter, depending on the specific driver and data source.

        logger.info(f'value from ogr.Open([{self.file}]): [{value}]')

        if value:
            self.datasource = value
        else:
            raise ValueError(f'Unable to read file: [{self.file}]')

    def layers(self) -> Iterable[base.LayerReader]:
        """Iterates through the layers in the GIS file.

        Yields:
            base.Layer: Layer read from the GIS file.
        """
        # Read layer count
        layers: int = utils.raise_if_none(
            value=self.datasource.GetLayerCount(),
            message=f"Could not determine number of layers in file '{self.file}'",
        )

        # Loop through layers
        for layer_index in range(layers):
            # Read layer
            layer: ogr.Layer = utils.raise_if_none(
                value=self.datasource.GetLayerByIndex(layer_index),
                message=f"Could not read layer {layer_index} in file '{self.file}'",
            )

            # Instantiate layer reader
            reader = self.reader(self.file, self.datasource, layer)

            # Check whether this layer should be skipped
            # Some formats use layers to store extra metadata
            if reader.skip():
                # Continue
                continue

            # Yield
            yield reader
            
    def layer_count(self) -> int:
        return utils.raise_if_none(
            value=self.datasource.GetLayerCount(),
            message=f"Could not determine number of layers in file '{self.file}'",
        )
