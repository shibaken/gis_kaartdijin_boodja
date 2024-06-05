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

from govapp.gis.readers.formats.geotiff import GeoTiffReader

# Logging
log = logging.getLogger(__name__)


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
        self.file = compression.decompress(self.file)
        self.file = compression.flatten(self.file)

        # Get layer reader class
        self.reader = utils.get_reader(self.file)
            
        # Load data source
        if self.reader == GeoTiffReader:
            value = gdal.Open(self.file, gdal.GA_ReadOnly)
            self._log_metadata(value)
        else:
            value = ogr.Open(str(self.file))

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

    def _log_metadata(dataset):
        # Get the metadata
        metadata = dataset.GetMetadata() 

        # Display the metadata
        for key, value in metadata.items(): 
            log.info(f"{key}: {value}") 

        # Resolution information
        x_resolution = dataset.GetGeoTransform()[1] # X Resolution
        y_resolution = dataset.GetGeoTransform()[5] # Y Resolution (often negative values)
        log.info(f"X Resolution: {x_resolution}") 
        log.info(f"Y Resolution: {y_resolution}") 

        # Get the number of bands
        bands = dataset.RasterCount 
        log.info(f"Number of bands: {bands}") 

        # Example of obtaining metadata for each band
        for i in range(1, bands + 1): 
            band = dataset.GetRasterBand(i) 
            band_metadata = band.GetMetadata() 
            log.info(f"Band {i} metadata:") 
            for key, value in band_metadata.items(): 
                log.info(f" {key}: {value}") 

        # Get the projection information
        projection = dataset.GetProjection() 
        log.info(f"Projection: {projection}") 

        # Corner coordinates (e.g., geographic coordinates of the upper left corner)
        geo_transform = dataset.GetGeoTransform() 
        origin_x = geo_transform[0] 
        origin_y = geo_transform[3] 
        log.info(f"Origin: ({origin_x}, {origin_y})")
