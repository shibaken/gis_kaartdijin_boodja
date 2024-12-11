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


def to_geopackage(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str):
    """Converts a GIS file to the GeoPackage format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoPackage file.
    """
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoPackage...")

    try:
        # Decompress and Flatten if Required
        filepath = compression.decompress(filepath)
        filepath = compression.flatten(filepath)

        # Construct Output Filepath
        output_dir = tempfile.mkdtemp()
        output_filepath = pathlib.Path(output_dir) / f"{layer}.gpkg"

        if export_method =='geoserver':
            command = [
                "ogr2ogr",
                "-overwrite",
                str(output_filepath),
                str(filepath),
                str(layer),
                "-nln",
                str(layer),
            ]
        else:
            command = [
                "ogr2ogr",
                "-update",
                "-overwrite",
                "-nln", 
                str(layer),                 #'Name' box in new CDDP dialogue
                str(output_filepath),
                str(filepath),              
                str(catalogue_name)         # Catalogue name
            ]
        log.info(f"Running command: [{' '.join(command)}]")

        # Run the command
        subprocess.check_call(command)
        log.info(f"Converted file [{filepath}], layer: [{layer}] to GeoPackage successfully.")
        
        converted = {"uncompressed_filepath": output_filepath.parent, "full_filepath": output_filepath,  "orignal_filepath": filepath}
        log.info(f'converted: [{converted}]')

        return converted

    except subprocess.TimeoutExpired as e:
        log.error(f"The command has reached a timeout. Error converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
        raise RuntimeError(f"Timeout error converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
    except subprocess.CalledProcessError as e:
        log.error(f"CalledProcessError: Error converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
        raise RuntimeError(f"CalledProcessError converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: Error converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
        raise RuntimeError(f"FileNotFoundError converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
    except Exception as e:
        log.error(f"Unexpected error converting file '{filepath}' layer: '{layer}' to GeoPackage: {e}")
        raise


def to_geojson(filepath: pathlib.Path, layer: str, catalogue_name: str = '', export_method: str = '') -> pathlib.Path:
    """Converts a GIS file to the GeoJSON format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoJSON file.
    """
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoJSON...")

    try:
        # Decompress and Flatten if Required
        filepath = compression.decompress(filepath)
        filepath = compression.flatten(filepath)

        # Construct Output Filepath
        output_dir = tempfile.mkdtemp()
        output_filepath = pathlib.Path(output_dir) / f"{layer}.geojson"

        command = [
            "ogr2ogr",
            "-unsetFid",
            str(output_filepath),
            str(filepath),
            str(layer),
        ]
        log.info(f"Running command: [{' '.join(command)}]")

        # Run the command
        subprocess.check_call(  # noqa: S603,S607
            command,
            timeout=1800,  # 30min
        )
        log.info(f"Converted file [{filepath}], layer: [{layer}] to GeoJSON successfully.")

        return pathlib.Path(output_filepath)

    except subprocess.TimeoutExpired as e:
        log.error(f"The command has reached a timeout.  Error converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
        raise RuntimeError(f"Error converting file '{filepath}' layer: '{layer}' to GeoJSON")
    except subprocess.CalledProcessError as e:
        log.error(f"Error converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
        raise RuntimeError(f"Error converting file '{filepath}' layer: '{layer}' to GeoJSON")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: Error converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
        raise RuntimeError(f"FileNotFoundError converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
    except Exception as e:
        log.error(f"Unexpected error converting file '{filepath}' layer: '{layer}' to GeoJSON: {e}")
        raise


def to_shapefile(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str):
    """Converts a GIS file to the ShapeFile format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted ShapeFile file.
    """
    log.info(f"Converting file '{filepath}' layer: '{layer}' to ShapeFile...")

    try:
        # Decompress and Flatten if Required
        filepath = compression.decompress(filepath)
        filepath = compression.flatten(filepath)

        # Construct Output Filepath
        # Here we double up on the `layer.shp` to ensure its in a directory
        output_dir = tempfile.mkdtemp()
        output_filepath = pathlib.Path(output_dir) / f"{layer}.shp"
        output_filepath.mkdir(parents=True, exist_ok=True)
        output_filepath = output_filepath / f"{layer}.shp"

        command = [
            "ogr2ogr",
            "-overwrite",
            "-unsetFid",
            str(output_filepath),
            str(filepath),        
            str(catalogue_name)
        ]
        log.info(f"Running command: [{' '.join(command)}]")

        # Run the command
        subprocess.check_call(command)
        log.info(f"Converted file [{filepath}], layer: [{layer}] to Shapefile successfully.")

        # Compress!
        compressed_filepath = compression.compress(output_filepath.parent)
        converted = {"compressed_filepath" : compressed_filepath, "uncompressed_filepath": output_filepath.parent}
        log.info(f'converted: [{converted}]')

        return converted

    except subprocess.TimeoutExpired as e:
        log.error(f"The command has reached a 30-minute timeout.  Error converting file '{filepath}' layer: '{layer}' to Shapefile: {e}")
        raise RuntimeError(f"Error converting file '{filepath}' layer: '{layer}' to Shapefile")
    except subprocess.CalledProcessError as e:
        log.error(f"Error converting file '{filepath}' layer: '{layer}' to Shapefile: {e}")
        raise RuntimeError(f"Error converting file '{filepath}' layer: '{layer}' to Shapefile")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: Error converting file '{filepath}' layer: '{layer}' to Shapefile: {e}")
        raise RuntimeError(f"FileNotFoundError converting file '{filepath}' layer: '{layer}' to Shapefile: {e}")
    except Exception as e:
        log.error(f"Unexpected error converting file '{filepath}' layer: '{layer}' to Shapefile: {e}")
        raise



def to_geodatabase(filepath: pathlib.Path, layer: str, catalogue_name: str, export_method: str):
    """Converts a GIS file to the GeoDatabase format.

    Args:
        filepath (pathlib.Path): Path to the file to be converted.
        layer (str): Layer to be converted.

    Returns:
        pathlib.Path: Path to the converted GeoDatabase file.
    """
    log.info(f"Converting file '{filepath}' layer: '{layer}' to GeoDatabase...")

    try:
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

        # Construct the command
        command = [
            "ogr2ogr",
            "-update",
            "-overwrite",
            "-nln", 
            str(layer),
            str(output_filepath),
            str(filepath),
            str(layer)
        ]
        log.info(f"Running command: [{' '.join(command)}]")

        # Run the command
        subprocess.check_call(command)
        log.info(f"Converted file [{filepath}], layer: [{layer}] to GeoDatabase successfully.")

        # Compress!
        compressed_filepath = compression.compress(output_filepath.parent)
        converted = {"compressed_filepath" : compressed_filepath, "uncompressed_filepath": output_filepath.parent, "orignal_filepath": filepath, "filepath_before_flatten": filepath_before_flatten}
        log.info(f'converted: [{converted}]')

        # Return
        return converted

    except subprocess.TimeoutExpired as e:
        log.error(f"The command has reached a 30-minute timeout. Error converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
        raise RuntimeError(f"Timeout error converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
    except subprocess.CalledProcessError as e:
        log.error(f"CalledProcessError: Error converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
        raise RuntimeError(f"CalledProcessError converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: Error converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
        raise RuntimeError(f"FileNotFoundError converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
    except Exception as e:
        log.error(f"Unexpected error converting file '{filepath}' layer: '{layer}' to GeoDatabase: {e}")
        raise


def postgres_to_shapefile(layer_name: str, hostname: str, username: str, password: str, database:  str, port: str,sqlquery: str): 
    log.info(f"Converting custom query for the PostGIS to shapefile...")

    try:
        converted = {}
        output_dir = tempfile.mkdtemp()
        cleaned_sqlquery = sqlquery.replace('\n', ' ')

        command = [
            "pgsql2shp",
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
        ]
        log.info(f"Running command: [{' '.join(command)}]")

        subprocess.check_call(
            command,
            cwd=output_dir
        )
        log.info(f"Converted custom query for the PostGIS to shapefile successfully.")
        
        compressed_filepath = compression.compress(pathlib.Path(output_dir))
        converted["output_dir"] = output_dir
        converted["compressed_filepath"] = str(compressed_filepath)
        log.info(f'converted: [{converted}]')

        return converted 

    except subprocess.TimeoutExpired as e:
        log.error(f"The command has reached a timeout. Error converting custom query for the PostGIS to shapefile: {e}")
        raise RuntimeError(f"Timeout error converting custom query for the PostGIS to shapefile: {e}")
    except subprocess.CalledProcessError as e:
        log.error(f"CalledProcessError: Error converting custom query for the PostGIS to shapefile: {e}")
        raise RuntimeError(f"CalledProcessError converting custom query for the PostGIS to shapefile: {e}")
    except FileNotFoundError as e:
        log.error(f"FileNotFoundError: Error converting custom query for the PostGIS to shapefile: {e}")
        raise RuntimeError(f"FileNotFoundError converting custom query for the PostGIS to shapefile: {e}")
    except Exception as e:
        log.error(f"Unexpected error converting custom query for the PostGIS to shapefile: {e}")
        raise


def convert_tiff_to_geopackage(input_tiff, output_gpkg, output_layer_name):
    """
    Converts a TIFF file to a GeoPackage file.

    Parameters:
    input_tiff (str): Path to the input TIFF file.
    output_gpkg (str): Path to the output GeoPackage file.
    output_layer_name (str): Name of the layer to be added in the GeoPackage.

    """
    log.info(f"Converting tiff file: [{input_tiff}] to GeoDatabase...")

    try:
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

        log.info(f'Converted tiff file: [{input_tiff}] to GeoPackage successfully.')

    except ValueError as e:
        log.error(f"ValueError: {e}")
        raise
    except RuntimeError as e:
        log.error(f"RuntimeError: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error converting tiff file '{input_tiff}' to GeoPackage: {e}")
        raise