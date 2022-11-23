"""Base class for determining GIS layers."""


# Standard
import abc
import pathlib


class LayerAnalyser(abc.ABC):
    """Layer Analyser Protocol."""

    # Class Variables
    filetypes: tuple[str, ...] = NotImplemented  # Must be implemented

    def __init_subclass__(cls) -> None:
        """Registers subclass and its filetypes."""
        # Loop through assigned filetypes
        for filetype in cls.filetypes:
            # Check filetype
            if filetype not in analysers:
                # Add new set to the analysers dictionary
                analysers[filetype] = set()

            # Register class for that filetype
            analysers[filetype.lower()].add(cls)

    def __init__(self, file: pathlib.Path) -> None:
        """Instantiates the Layer Analyser.

        Args:
            file (pathlib.Path): Filepath to extract attributes from.
        """
        # Instance attributes
        self.file = file

    @abc.abstractmethod
    def layers(self) -> list[str]:
        """Determines number of layers.

        Returns:
            list[str]: List of layers in the GIS file.
        """
        # Must be implemented on subclass
        raise NotImplementedError


# Extractors Registry
analysers: dict[str, set[type[LayerAnalyser]]] = {}
