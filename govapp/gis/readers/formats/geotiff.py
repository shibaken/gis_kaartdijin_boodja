"""GeoTiff Reader."""


# Standard
import pathlib

# Local
from govapp.gis.readers import base


class GeoTiffReader(base.LayerReader):
    """Geotiff Layer Reader."""

    @classmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether this file is a GeoTiff file.

        Args:
            file (pathlib.Path): Path to the file to check.

        Returns:
            bool: Whether this file is compatible with this reader.
        """
        # Check and Return
        # Path must be a file with the suffix `.json` or `.geojson`
        return file.is_file() and file.suffix.lower() in (".tif", ".tiff")
