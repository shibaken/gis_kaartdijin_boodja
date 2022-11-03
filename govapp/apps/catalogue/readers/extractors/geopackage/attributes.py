"""Geopackage GIS Attribute Extractor."""


# Standard
import sqlite3

# Local
from ... import base
from ... import types


class GeopackageAttributeExtractor(base.attributes.AttributeExtractor):
    """Geopackage Attribute Extractor."""

    # Filetypes
    filetypes = (".gpkg", )

    def attributes(self, layer: str) -> list[types.attributes.Attribute]:
        """Extracts attributes from a Geopackage file.

        Args:
            layer (str): Layer name to retrieve the attributes from.

        Returns:
            list[models.attributes.Attribute]: List of extracted attributes.
        """
        # Retrieve a connection and cursor from the file
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()

        # Perform the queries
        results = cursor.execute(
            "SELECT cid,name,type "
            "FROM PRAGMA_TABLE_INFO(:layer) ",
            {"layer": layer}
        ).fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Construct attributes list
        attributes = [  # noqa A001
            types.attributes.Attribute(name, type, cid + 1)
            for (cid, name, type) in results
        ]

        # Return attributes
        return attributes
