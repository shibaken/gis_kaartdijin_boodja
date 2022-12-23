"""GeoDatabase GIS Reader."""


# Standard
import pathlib

# Local
from .. import base
from .. import utils


class GeoDatabaseReader(base.LayerReader):
    """GeoDatabase Layer Reader."""

    @classmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether this file is a GeoDatabase directory.

        Args:
            file (pathlib.Path): Path to the file to check.

        Returns:
            bool: Whether this file is compatible with this reader.
        """
        # Check and Return
        # Path must be a directory and must contain a file called `gdb`
        return file.is_dir() and utils.exists(file.glob("gdb"))
