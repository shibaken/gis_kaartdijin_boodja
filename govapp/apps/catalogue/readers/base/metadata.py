"""Base class for extracting GIS Metadata."""


# Standard
import abc
import pathlib

# Local
from .. import types


class MetadataExtractor(abc.ABC):
    """Metadata Extractor Protocol."""

    # Class Variables
    filetypes: tuple[str, ...] = NotImplemented  # Must be implemented

    def __init_subclass__(cls) -> None:
        """Registers subclass and its filetypes."""
        # Loop through assigned filetypes
        for filetype in cls.filetypes:
            # Check filetype
            if filetype not in extractors:
                # Add new set to the extractors dictionary
                extractors[filetype] = set()

            # Register class for that filetype
            extractors[filetype.lower()].add(cls)

    def __init__(self, file: pathlib.Path) -> None:
        """Instantiates the Metadata Extractor.

        Args:
            file (pathlib.Path): Filepath to extract metadata from.
        """
        # Instance attributes
        self.file = file

    @abc.abstractmethod
    def metadata(self, layer: str) -> types.metadata.Metadata:
        """Extracts metadata.

        Args:
            layer (str): Layer name to retrieve the metadata from.

        Returns:
            models.metadata.Metadata: Extracted metadata.
        """
        # Must be implemented on subclass
        raise NotImplementedError


# Extractors Registry
extractors: dict[str, set[type[MetadataExtractor]]] = {}
