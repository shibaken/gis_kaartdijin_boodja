"""Provides unit tests for the GIS conversions module."""


# Standard
import yaml

# Local
from govapp.gis import conversions
from tests import utils

# Third-Party
import pytest


@pytest.mark.parametrize(
    (
        "data_file",
        "yaml_file",
    ),
    [
        ("gdb/100kMapsheetIndex_sgl_lyr.gdb.7z", "gdb/100kMapsheetIndex_sgl_lyr.gdb.yaml"),
        ("gdb/GDB_4lyr_w_2_sld.7z", "gdb/GDB_4lyr_w_2_sld.yaml"),
        ("gdb/Plantations_4_layers.gdb.7z", "gdb/Plantations_4_layers.gdb.yaml"),
        ("geojson/regions.geojson", "geojson/regions.yaml"),
        ("gpkg/Admin_boundaries.gpkg", "gpkg/Admin_boundaries.yaml"),
        ("gpkg/Local_areas_styled.gpkg", "gpkg/Local_areas_styled.yaml"),
        ("gpkg/WA_coast.gpkg", "gpkg/WA_coast.yaml"),
        ("shp/cog_index_w_sld.7z", "shp/cog_index_w_sld.yaml"),
        ("shp/World_Heritage.7z", "shp/World_Heritage.yaml"),
    ],
)
def test_to_geopackage(data_file: str, yaml_file: str) -> None:
    """Tests the reading of parametrized GIS files."""
    # Filepath
    data_filepath = utils.test_file(data_file)
    yaml_filepath = utils.test_file(yaml_file)

    # Load YAML File
    expected = yaml.safe_load(yaml_filepath.open())
    expected = expected["layers"]

    # Copy to a Temporary Directory
    temporary_filepath = utils.to_temporary_directory(data_filepath)

    # Loop through layers
    for layer in expected:
        # Convert
        result = conversions.to_geopackage(
            filepath=temporary_filepath,
            layer=layer["name"],
        )

        # Check file exists
        assert result.exists()
