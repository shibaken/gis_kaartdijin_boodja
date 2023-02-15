"""GeoDatabase GIS Reader."""


# Standard
import pathlib

# Local
from govapp.gis import utils
from govapp.gis.readers import base
from govapp.gis.readers import types


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

    def symbology(self) -> types.Symbology:
        """Extracts symbology.

        Returns:
            models.Symbology: Extracted symbology.
        """
        # For geodatabases, there is sometimes an `.sld` file included which
        # has the same filename as the layer. As demonstrated in the test data,
        # these `.sld` files are at the same level as the `.gdb` folder - which
        # means we need to look for and retrieve it at the file's parent.
        sld_path = (self.file.parent / self.name).with_suffix(".sld")

        # Check if the file exists
        if sld_path.exists() and sld_path.is_file():
            # Construct and Return Symbology
            return types.Symbology(
                name=self.name,  # Just use the name of the layer
                sld=sld_path.read_text(),  # Read the SLD file
            )

        # Raise
        return super().symbology()
