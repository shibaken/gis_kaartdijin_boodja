"""Geopackage GIS Reader."""


# Standard
import datetime
import pathlib

# Local
from .. import base
from .. import types
from .. import utils

# Third-Party
from dateutil import parser
from osgeo import ogr


class GeopackageReader(base.LayerReader):
    """Geopackage Layer Reader."""

    @classmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether this file is a Geopackage file.

        Args:
            file (pathlib.Path): Path to the file to check.

        Returns:
            bool: Whether this file is compatible with this reader.
        """
        # Check and Return
        return file.suffix.lower() == ".gpkg"

    def skip(self) -> bool:
        """Determines whether to skip this layer.

        Some Geopackage files (e.g., created by QGIS) have an extra layer
        called `layer_styles` which is not actually a layer - it stores the
        symbology for the other layers. If we encounter this layer, then we
        skip it.

        Returns:
            bool: Whether to skip this layer.
        """
        # Check and Return
        return self.name == "layer_styles"

    def attributes(self) -> list[types.Attribute]:
        """Extracts attributes.

        Returns:
            list[models.Attribute]: List of extracted attributes.
        """
        # Construct Attributes List
        attributes: list[types.Attribute] = []

        # Get Layer Definition
        layer_defn: ogr.FeatureDefn = self.layer.GetLayerDefn()

        # Get Attributes Count
        attributes_count = layer_defn.GetFieldCount()

        # Loop through Attribute Indexes
        for attribute_index in range(attributes_count):
            # Get Attribute Definition
            attribute_defn: ogr.FieldDefn = layer_defn.GetFieldDefn(attribute_index)

            # Construct Attribute
            attribute = types.Attribute(
                name=attribute_defn.GetName(),
                type=attribute_defn.GetFieldTypeName(attribute_defn.GetType()),
                order=attribute_index + 1,
            )

            # Append Attribute
            attributes.append(attribute)

        # Return
        return attributes

    def metadata(self) -> types.Metadata:
        """Extracts metadata.

        Returns:
            models.Metadata: Extracted metadata.
        """
        # Extract Name and Description from Metadata
        name = self.layer.GetMetadataItem("IDENTIFIER") or self.layer.GetName()
        description = self.layer.GetMetadataItem("DESCRIPTION") or ""  # Blank

        # Handle Errors
        try:
            # Extract Last Change Datetime with SQL
            layer: ogr.Layer = self.datasource.ExecuteSQL(
                "SELECT last_change "  # noqa: S608
                "FROM gpkg_contents "
                f"WHERE table_name = '{self.layer.GetName()}'"
            )
            feature: ogr.Feature = layer.GetNextFeature()
            field: str = feature.GetField(0)
            created_at = parser.parse(field)

        except Exception:
            # Use Current Time (UTC)
            created_at = datetime.datetime.now(datetime.timezone.utc)

        # Construct and Return Metadata
        return types.Metadata(
            name=name,
            description=description,
            created_at=created_at,
        )

    def symbology(self) -> types.Symbology:
        """Extracts symbology.

        Returns:
            models.Symbology: Extracted symbology.
        """
        # Precompute error message
        message = f"Could not extract symbology for layer {self.layer.GetName()}"

        # Extract Symbology with from Layer Styles Table
        layer: ogr.Layer = utils.raise_if_none(
            value=self.datasource.GetLayerByName("layer_styles"),
            message=message,
        )

        # Filter
        layer.SetAttributeFilter(f"f_table_name = '{self.layer.GetName()}'")

        # Get Feature
        feature: ogr.Feature = utils.raise_if_none(
            value=layer.GetNextFeature(),
            message="A",
        )

        # Get Style Name and SLD Indexes
        name_index: int = utils.raise_if_none(
            value=feature.GetFieldIndex("styleName"),
            message=message,
        )
        sld_index: int = utils.raise_if_none(
            value=feature.GetFieldIndex("styleSLD"),
            message=message,
        )

        # Get Style Name and SLD
        name: str = utils.raise_if_none(
            value=feature.GetField(name_index),
            message=message,
        )
        sld: str = utils.raise_if_none(
            value=feature.GetField(sld_index),
            message=message,
        )

        # Construct and Return Symbology
        return types.Symbology(
            name=name,
            sld=sld,
        )
