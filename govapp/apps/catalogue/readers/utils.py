"""GIS Reader Utilities."""


# Standard
import pathlib

# Local
from . import base

# Typing
from typing import Optional, TypeVar


# Type Variables
T = TypeVar("T")


def raise_if_none(value: Optional[T], message: str) -> T:
    """Checks if a value is None and raises an error if it is.

    Args:
        value (Optional[T]): Value to check.
        message (str): Error message if the value is None.

    Raises:
        ValueError: Raised if the value is None.

    Returns:
        T: The unwrapped value if not None.
    """
    # Check Value
    if value is None:
        # Raise
        raise ValueError(message)

    # Return
    return value


def get_reader(file: pathlib.Path) -> type[base.LayerReader]:
    """Retrieves a compatible Layer Reader for this file type.

    Args:
        file (pathlib.Path): Path to the file to read.

    Returns:
        base.LayerReader: The determined compatible Layer Reader.

    Raises:
        ValueError: Raised if a compatible Layer Reader cannot be found.
    """
    # Loop through Layer Readers
    for reader in base.readers:
        # Check if this reader is compatible
        if reader.is_compatible(file):
            # Return the reader class
            return reader

    # Raise
    raise ValueError(
        f"Could not find any compatible readers for '{file.suffix}' files"
    )
