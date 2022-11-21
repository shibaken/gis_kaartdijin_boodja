"""Base class for extracting GIS Attributes."""


# Standard
import abc
import pathlib

# Local
from .. import types


class AttributeExtractor(abc.ABC):
    """Attribute Extractor Protocol."""

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
        """Instantiates the Attribute Extractor.

        Args:
            file (pathlib.Path): Filepath to extract attributes from.
        """
        # Instance attributes
        self.file = file

    @abc.abstractmethod
    def attributes(self, layer: str) -> list[types.attributes.Attribute]:
        """Extracts attributes.

        Args:
            layer (str): Layer name to retrieve the attributes from.

        Returns:
            list[models.attributes.Attribute]: List of extracted attributes.
        """
        # Must be implemented on subclass
        raise NotImplementedError


# Extractors Registry
extractors: dict[str, set[type[AttributeExtractor]]] = {}
