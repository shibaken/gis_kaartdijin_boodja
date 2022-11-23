"""Geopackage GIS Metadata Extractor."""


# Standard
import sqlite3

# Third-Party
import dateutil.parser

# Local
from ... import base
from ... import types


class GeopackageMetadataExtractor(base.metadata.MetadataExtractor):
    """Geopackage Metadata Extractor."""

    # Filetypes
    filetypes = (".gpkg", )

    def metadata(self, layer: str) -> types.metadata.Metadata:
        """Extracts metadata from a Geopackage file.

        Args:
            layer (str): Layer name to retrieve the metadata from.

        Returns:
            models.metadata.Metadata: Extracted metadata.
        """
        # Retrieve a connection and cursor from the file
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()

        # Perform the queries
        results = cursor.execute(
            "SELECT identifier,description,last_change "
            "FROM gpkg_contents "
            "WHERE table_name = :layer",
            {"layer": layer}
        ).fetchone()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Check results
        assert results is not None  # noqa: S101

        # Construct metadata
        metadata = types.metadata.Metadata(
            name=results[0],
            description=results[1],
            created_at=dateutil.parser.isoparse(results[2])
        )

        # Return metadata
        return metadata
