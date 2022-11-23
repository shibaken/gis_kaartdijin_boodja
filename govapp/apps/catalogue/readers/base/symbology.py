"""Base class for extracting GIS Symbology."""


# Standard
import abc
import pathlib

# Local
from .. import types


class SymbologyExtractor(abc.ABC):
    """Symbology Extractor Protocol."""

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
        """Instantiates the Symbology Extractor.

        Args:
            file (pathlib.Path): Filepath to extract symbology from.
        """
        # Instance attributes
        self.file = file

    @abc.abstractmethod
    def symbology(self, layer: str) -> types.symbology.Symbology:
        """Extracts symbology.

        Args:
            layer (str): Layer name to retrieve the symbology from.

        Returns:
            models.symbology.Symbology: Extracted symbology.
        """
        # Must be implemented on subclass
        raise NotImplementedError


# Extractors Registry
extractors: dict[str, set[type[SymbologyExtractor]]] = {}
