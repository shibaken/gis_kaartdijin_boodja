"""Geopackage GIS Layer Analyser."""


# Standard
import sqlite3

# Local
from ... import base


class GeopackageLayerAnalyser(base.layers.LayerAnalyser):
    """Geopackage Layer Analyser."""

    # Filetypes
    filetypes = (".gpkg", )

    def layers(self) -> list[str]:
        """Determines number of layers in a Geopackage file.

        Returns:
            list[str]: Layers in the Geopackage file.
        """
        # Retrieve a connection and cursor from the file
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()

        # Perform the queries
        results = cursor.execute(
            "SELECT table_name "
            "FROM gpkg_contents "
            "WHERE data_type = 'features'"
        ).fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Reformat the results
        # The output of the above is a list of tuples
        results = [r[0] for r in results]

        # Return number of layers
        return results
