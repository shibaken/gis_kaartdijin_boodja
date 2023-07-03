"""GIS Conversion Functionality."""


# Standard
import logging
import pathlib
import subprocess  # noqa: S404
import tempfile

# Local
from govapp.gis import compression


# Logging
log = logging.getLogger(__name__)


def to_geopackage(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str) -> pathlib.Path:
    """Converts a GIS file to the GeoPackage format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoPackage file.
    """
    # Log
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoPackage")

    # Decompress and Flatten if Required
    filepath = compression.decompress(filepath)
    filepath = compression.flatten(filepath)

    # Construct Output Filepath
    output_dir = tempfile.mkdtemp()
    output_filepath = pathlib.Path(output_dir) / f"{layer}.gpkg"

    if export_method =='geoserver':
        subprocess.check_call(
            [
                "ogr2ogr",
                "-overwrite",
                str(output_filepath),
                str(filepath),
                str(layer),
                "-nln",
                str(layer),
            ]
        )

    else:
        # Run Command
        subprocess.check_call(  # noqa: S603,S607
            [
                "ogr2ogr",
                "-update",
                "-overwrite",
                "-nln", 
                str(layer),                 #'Name' box in new CDDP dialogue
                str(output_filepath),
                str(filepath),              
                str(catalogue_name)         # Catalogue name
            ]


        )
    converted = {"uncompressed_filepath": output_filepath.parent, "full_filepath": output_filepath}
    # Return
    return converted
    #return output_filepath


def to_geojson(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str) -> pathlib.Path:
    """Converts a GIS file to the GeoJSON format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoJSON file.
    """
    # Log
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoJSON")

    # Decompress and Flatten if Required
    filepath = compression.decompress(filepath)
    filepath = compression.flatten(filepath)

    # Construct Output Filepath
    output_dir = tempfile.mkdtemp()
    output_filepath = pathlib.Path(output_dir) / f"{layer}.geojson"

    # Run Command
    subprocess.check_call(  # noqa: S603,S607
        [
            "ogr2ogr",
            "-unsetFid",
            str(output_filepath),
            str(filepath),            
            str(layer),
        ]
    )
    # converted = {"uncompressed_filepath": output_filepath.parent, "full_filepath": output_filepath}
    # Return
    return pathlib.Path(output_filepath)
    #return output_filepath


def to_shapefile(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str) -> pathlib.Path:
    """Converts a GIS file to the ShapeFile format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted ShapeFile file.
    """
    # Log
    log.info(f"Converting file '{filepath}' layer: '{layer}' to ShapeFile")

    # Decompress and Flatten if Required
    filepath = compression.decompress(filepath)
    filepath = compression.flatten(filepath)

    # Construct Output Filepath
    # Here we double up on the `layer.shp` to ensure its in a directory
    output_dir = tempfile.mkdtemp()
    output_filepath = pathlib.Path(output_dir) / f"{layer}.shp"
    output_filepath.mkdir(parents=True, exist_ok=True)
    output_filepath = output_filepath / f"{layer}.shp"

    # Run Command
    subprocess.check_call(  # noqa: S603,S607
        [
            "ogr2ogr",
            "-overwrite",
            "-unsetFid",
            str(output_filepath),
            str(filepath),        
            str(catalogue_name),
        ]
    )

    # Compress!
    compressed_filepath = compression.compress(output_filepath.parent)
    converted = {"compressed_filepath" : compressed_filepath, "uncompressed_filepath": output_filepath.parent}

    # Return
    return converted


def to_geodatabase(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str) -> pathlib.Path:
    """Converts a GIS file to the GeoDatabase format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoDatabase file.
    """
    # Log
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoDatabase")

    # Decompress and Flatten if Required
    filepath = compression.decompress(filepath)
    filepath = compression.flatten(filepath)

    # Construct Output Filepath
    # Here we double up on the `layer.gdb` to ensure its in a directory
    output_dir = tempfile.mkdtemp()
    output_filepath = pathlib.Path(output_dir) / f"{layer}.gdb"
    output_filepath.mkdir(parents=True, exist_ok=True)
    output_filepath = output_filepath / f"{layer}.gdb"

    # Run Command
    subprocess.check_call(  # noqa: S603,S607
        # [
        #     "ogr2ogr",
        #     "-overwrite",
        #     "-append",
        #     str(output_filepath),
        #     str(filepath),
        #     "-nln",
        #     str(layer),
        # ]
        [
        "ogr2ogr",
        "-update",
        "-overwrite",
        "-nln", 
        str(layer),
        str(output_filepath),
        str(filepath),
        str(layer)
        ]


    )

    # Compress!
    #compressed_filepath = compression.compress(output_filepath.parent)

    compressed_filepath = compression.compress(output_filepath.parent)
    converted = {"compressed_filepath" : compressed_filepath, "uncompressed_filepath": output_filepath.parent}
    # Return
    return converted
    #return compressed_filepath
