"""GIS Conversion Functionality."""


# Standard
import logging
import pathlib
import subprocess  # noqa: S404
import tempfile
from osgeo import gdal

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
    converted = {"uncompressed_filepath": output_filepath.parent, "full_filepath": output_filepath,  "orignal_filepath": filepath}

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
    try:
        subprocess.check_call(  # noqa: S603,S607
            [
                "ogr2ogr",
                "-unsetFid",
                str(output_filepath),
                str(filepath),            
                str(layer),
            ]
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Error converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
        raise RuntimeError(f"Error converting file '{filepath}' layer: '{layer}' to GeoJSON")

    return pathlib.Path(output_filepath)


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
    filepath_before_flatten = filepath
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
    converted = {"compressed_filepath" : compressed_filepath, "uncompressed_filepath": output_filepath.parent, "orignal_filepath": filepath, "filepath_before_flatten": filepath_before_flatten}
    # Return
    return converted
    #return compressed_filepath


def postgres_to_shapefile(layer_name: str, hostname: str, username: str, password: str, database:  str, port: str,sqlquery: str) -> pathlib.Path: 
    hash_array = {}
    output_dir = tempfile.mkdtemp()
    cleaned_sqlquery = sqlquery.replace('\n', ' ')

    subprocess.check_call(
        ["pgsql2shp",
        "-f",
        layer_name,
        "-h", 
        str(hostname),
        "-u", 
        str(username),
        "-p",
        str(port),
        "-P",
        str(password),
        str(database),
        # str(sqlquery)
        str(cleaned_sqlquery)
        ],
        cwd=output_dir
    )
    
    compressed_filepath = compression.compress(output_dir)
    hash_array["output_dir"] = output_dir
    hash_array["compressed_filepath"] = compressed_filepath
    return hash_array 


def convert_tiff_to_geopackage(input_tiff, output_gpkg, output_layer_name):
    """
    Converts a TIFF file to a GeoPackage file.

    Parameters:
    input_tiff (str): Path to the input TIFF file.
    output_gpkg (str): Path to the output GeoPackage file.
    output_layer_name (str): Name of the layer to be added in the GeoPackage.

    """
    # Open the input TIFF file
    tiff_dataset = gdal.Open(input_tiff)
    
    if tiff_dataset is None:
        raise ValueError("Failed to open the input TIFF file.")

    # Get the GeoPackage driver
    gpkg_driver = gdal.GetDriverByName("GPKG")
    
    if gpkg_driver is None:
        log.error("GeoPackage driver is not available.")
        raise ValueError("GeoPackage driver is not available.")

    # Create the GeoPackage file
    gpkg_dataset = gpkg_driver.Create(output_gpkg,
                                      tiff_dataset.RasterXSize,
                                      tiff_dataset.RasterYSize,
                                      tiff_dataset.RasterCount,
                                      gdal.GDT_Byte)
    
    if gpkg_dataset is None:
        log.error("Failed to create the GeoPackage file.")
        raise ValueError("Failed to create the GeoPackage file.")

    # Copy data from the TIFF file to the GeoPackage file
    for band_number in range(1, tiff_dataset.RasterCount + 1):
        band = tiff_dataset.GetRasterBand(band_number)
        gpkg_band = gpkg_dataset.GetRasterBand(band_number)
        gpkg_band.WriteArray(band.ReadAsArray())

    # Set the layer name in the GeoPackage file
    gpkg_dataset.SetMetadataItem("LAYERS", output_layer_name)

    # Close the GeoPackage file
    gpkg_dataset = None

    log.info("Converted TIFF file to GeoPackage successfully.")
