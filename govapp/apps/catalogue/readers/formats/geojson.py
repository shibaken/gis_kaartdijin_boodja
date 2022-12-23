"""GeoJSON GIS Reader."""


# Standard
import pathlib

# Local
from .. import base


class GeoJSONReader(base.LayerReader):
    """GeoJSON Layer Reader."""

    @classmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether this file is a GeoJSON file.

        Args:
            file (pathlib.Path): Path to the file to check.

        Returns:
            bool: Whether this file is compatible with this reader.
        """
        # Check and Return
        # Path must be a file with the suffix `.json`
        return file.is_file() and file.suffix.lower() == ".json"
