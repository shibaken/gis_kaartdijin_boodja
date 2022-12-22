"""Base class for reading GIS files."""


# Standard
import pathlib

# Third-Party
from osgeo import ogr

# Local
from . import base
from . import utils

# Typing
from typing import Iterable


class FileReader:
    """Reader Protocol."""

    def __init__(self, file: pathlib.Path) -> None:
        """Instantiates the GIS File Reader.

        Args:
            file (pathlib.Path): Filepath to read.
        """
        # Instance attributes
        self.file = file

        # Get layer reader class
        self.reader = utils.get_reader(self.file)

        # Load data source
        self.datasource: ogr.DataSource = utils.raise_if_none(
            value=ogr.Open(str(self.file)),
            message=f"Unable to read file '{self.file}'",
        )

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
