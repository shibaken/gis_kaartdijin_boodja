"""Geopackage GIS Symbology Extractor."""


# Standard
import sqlite3

# Local
from ... import base
from ... import types


class GeopackageSymbologyExtractor(base.symbology.SymbologyExtractor):
    """Geopackage Symbology Extractor."""

    # Filetypes
    filetypes = (".gpkg", )

    def symbology(self, layer: str) -> types.symbology.Symbology:
        """Extracts symbology from a Geopackage file.

        Args:
            layer (str): Layer name to retrieve the symbology from.

        Returns:
            models.symbology.Symbology: Extracted symbology.
        """
        # Retrieve a connection and cursor from the file
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()

        # Perform the queries
        results = cursor.execute(
            "SELECT styleName,styleSLD "
            "FROM layer_styles "
            "WHERE f_table_name = :layer",
            {"layer": layer}
        ).fetchone()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Check results
        assert results is not None  # noqa: S101

        # Construct symbology
        symbology = types.symbology.Symbology(
            name=results[0],
            sld=results[1],
        )

        # Return symbology
        return symbology
