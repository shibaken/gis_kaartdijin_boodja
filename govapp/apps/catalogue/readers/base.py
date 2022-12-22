"""Base class for reading GIS layers."""


# Standard
import abc
import pathlib

# Local
from . import types

# Third-Party
from osgeo import ogr


class LayerReader(abc.ABC):
    """Layer Reader Abstract Base Class."""

    def __init_subclass__(cls) -> None:
        """Registers subclass."""
        # Register subclass
        readers.add(cls)

    def __init__(
        self,
        file: pathlib.Path,
        datasource: ogr.DataSource,
        layer: ogr.Layer,
    ) -> None:
        """Instantiates the Layer Reader.

        Args:
            file (pathlib.Path): Filepath to read.
            datasource (ogr.DataSource): Interal OGR DataSource to be read.
            layer (ogr.Layer): Interal OGR Layer to be read.
        """
        # Instance Variables
        self.file = file
        self.datasource = datasource
        self.layer = layer

    @property
    def name(self) -> str:
        """Retrieves the name of the layer.

        Returns:
            str: Name of the layer.
        """
        # Retrieve and Return
        return self.layer.GetName()  # type: ignore[no-any-return]

    @classmethod
    @abc.abstractmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether the file and layer can be read.

        Args:
            file (pathlib.Path): Filepath to read.

        Returns:
            bool: Whether this Layer Reader can read the file and layer.
        """
        # Must be implemented on subclass
        raise NotImplementedError

    @abc.abstractmethod
    def skip(self) -> bool:
        """Determines whether to skip this layer.

        Returns:
            bool: Whether to skip this layer.
        """
        # Must be implemented on subclass
        raise NotImplementedError

    @abc.abstractmethod
    def attributes(self) -> list[types.Attribute]:
        """Extracts attributes.

        Returns:
            list[models.Attribute]: List of extracted attributes.
        """
        # Must be implemented on subclass
        raise NotImplementedError

    @abc.abstractmethod
    def metadata(self) -> types.Metadata:
        """Extracts metadata.

        Returns:
            models.Metadata: Extracted metadata.
        """
        # Must be implemented on subclass
        raise NotImplementedError

    @abc.abstractmethod
    def symbology(self) -> types.Symbology:
        """Extracts symbology.

        Returns:
            models.Symbology: Extracted symbology.
        """
        # Must be implemented on subclass
        raise NotImplementedError


# Readers Registry
readers: set[type[LayerReader]] = set()
