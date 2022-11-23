"""GIS Modular Readers Utilities."""


# Standard
import pathlib

# Local
from . import base
from . import types


def layers(file: pathlib.Path) -> list[str]:
    """Utility for automatically determining the number of layers in a file.

    Args:
        file (pathlib.Path): File to analyse layers from.

    Returns:
        list[str]: List of layers in the file.
    """
    # Get file suffix
    suffix = file.suffix.lower()

    # Retrieve layer analysers
    analysers = base.layers.analysers.get(suffix)

    # Check analysers
    if not analysers:
        # Raise Exception
        raise ValueError(
            f"Could not find any layer analysers for '{suffix}' files"
        )

    # List to store exceptions
    exceptions = []

    # Loop through analysers
    for analyser in analysers:
        # Handle errors
        try:
            # Analyse layers
            return analyser(file).layers()

        except Exception as exc:
            # Store exception for later
            exceptions.append(exc)

    # Raise Exception
    raise ValueError(
        f"Failed to analyse layers: {exceptions}"
    )


def attributes(
    file: pathlib.Path,
    layer: str,
) -> list[types.attributes.Attribute]:
    """Utility for automatically extracting attributes from a file.

    Args:
        file (pathlib.Path): File to extract attributes from.
        layer (str): Layer name to extract attributes from.

    Returns:
        list[types.attributes.Attribute]: The extracted attributes.
    """
    # Get file suffix
    suffix = file.suffix.lower()

    # Retrieve attribute extractors
    extractors = base.attributes.extractors.get(suffix)

    # Check extractors
    if not extractors:
        # Raise Exception
        raise ValueError(
            f"Could not find any attribute extractors for '{suffix}' files"
        )

    # List to store exceptions
    exceptions = []

    # Loop through extractors
    for extractor in extractors:
        # Handle errors
        try:
            # Extract attributes
            return extractor(file).attributes(layer)

        except Exception as exc:
            # Store exception for later
            exceptions.append(exc)

    # Raise Exception
    raise ValueError(
        f"Failed to extract attributes: {exceptions}"
    )


def metadata(
    file: pathlib.Path,
    layer: str,
) -> types.metadata.Metadata:
    """Utility for automatically extracting metadata from a file.

    Args:
        file (pathlib.Path): File to extract metadata from.
        layer (str): Layer name to extract metadata from.

    Returns:
        types.metadata.Metadata: The extracted metadata.
    """
    # Get file suffix
    suffix = file.suffix.lower()

    # Retrieve metadata extractors
    extractors = base.metadata.extractors.get(suffix)

    # Check extractors
    if not extractors:
        # Raise Exception
        raise ValueError(
            f"Could not find any metadata extractors for '{suffix}' files"
        )

    # List to store exceptions
    exceptions = []

    # Loop through extractors
    for extractor in extractors:
        # Handle errors
        try:
            # Extract metadata
            return extractor(file).metadata(layer)

        except Exception as exc:
            # Store exception for later
            exceptions.append(exc)

    # Raise Exception
    raise ValueError(
        f"Failed to extract metadata: {exceptions}"
    )


def symbology(
    file: pathlib.Path,
    layer: str,
) -> types.symbology.Symbology:
    """Utility for automatically extracting symbology from a file.

    Args:
        file (pathlib.Path): File to extract symbology from.
        layer (str): Layer name to extract symbology from.

    Returns:
        types.symbology.Symbology: The extracted symbology.
    """
    # Get file suffix
    suffix = file.suffix.lower()

    # Retrieve symbology extractors
    extractors = base.symbology.extractors.get(suffix)

    # Check extractors
    if not extractors:
        # Raise Exception
        raise ValueError(
            f"Could not find any symbology extractors for '{suffix}' files"
        )

    # List to store exceptions
    exceptions = []

    # Loop through extractors
    for extractor in extractors:
        # Handle errors
        try:
            # Extract symbology
            return extractor(file).symbology(layer)

        except Exception as exc:
            # Store exception for later
            exceptions.append(exc)

    # Raise Exception
    raise ValueError(
        f"Failed to extract symbology: {exceptions}"
    )
