"""GIS Compression Utilities."""


# Standard
import logging
import pathlib
import shutil
import tarfile
import zipfile
import datetime
import os

# Third-Party
import py7zr
import pytz
import rarfile

# Logging
log = logging.getLogger(__name__)


def compress(directory: pathlib.Path) -> pathlib.Path:
    """Compresses a directory.

    Args:
        directory (pathlib.Path): Directory to be compressed.

    Returns:
        pathlib.Path: Path to the compressed archive.
    """
    # Log
    log.info(f"Attemping to compress '{directory}'")

    # Compress!
    compressed_path = shutil.make_archive(
        base_name=str(directory),
        format="zip",
        root_dir=str(directory),
    )

    # Log
    log.info(f"Compressed '{directory}' -> '{compressed_path}'")

    # Return
    return pathlib.Path(compressed_path)


def decompress(file: pathlib.Path) -> pathlib.Path:
    """Decompresses a file and flattens it if required.

    Args:
        file (pathlib.Path): File to be decompressed.

    Returns:
        pathlib.Path: Path to the decompressed directory.
    """
    # Log
    log.info(f"Attemping to decompress '{file}' if required")

    # Check file
    algorithm = get_compressed_algorithm(file)

    # Check
    if not algorithm:
        log.info("No compression detected, leaving unchanged")
        return file  # Return the original filepath
    log.info(f"Detected compression: [{algorithm}]")

    if not os.path.exists('/tmp/gis_processing/'):
        os.makedirs('/tmp/gis_processing/')

    log.info(f"Preparing decompressing the file: [{file}]...")
    timestamp_str = datetime.datetime.now(pytz.utc).strftime("%Y%m%dT%H%M%S")

    # Construct Path for Extraction
    extracted_path = pathlib.Path("/tmp/gis_processing/extracted_" + file.stem + "_" + timestamp_str)
    log.info(f"Decompressing the file:[{file}] to the folder: [{extracted_path}]...")

    # Decompress
    with algorithm(file) as archive:
        archive.extractall(path=extracted_path)

    return extracted_path  # Return the path to the extracted directory


def get_compressed_algorithm(file):
    if zipfile.is_zipfile(file):
        # `.zip`
        algorithm = zipfile.ZipFile

    elif tarfile.is_tarfile(file):
        # `.tar`
        algorithm = tarfile.TarFile  # type: ignore

    elif rarfile.is_rarfile(file):
        # `.rar`
        algorithm = rarfile.RarFile

    elif py7zr.is_7zfile(file):
        # `.7z`
        algorithm = py7zr.SevenZipFile  # type: ignore

    else:
        # None!
        algorithm = None

    return algorithm # this is a path to the directory


def flatten(path: pathlib.Path) -> pathlib.Path:
    """Flattens a directory.

    Args:
        path (pathlib.Path): Directory to be flattened.

    Returns:
        pathlib.Path: Flattened directory.
    """
    # Log
    log.info(f"Attemping to flatten the directory: [{path}] if required")

    # Enumerate subdirectories
    subdirs = [p for p in path.glob("*") if p.is_dir()]

    # Check if there is a single directory inside
    if len(subdirs) == 1:
        # Log
        log.info(f"Flattened '{path}' -> {subdirs[0]}")

        # Recurse, flatten that directory also if applicable and return
        return flatten(subdirs[0])

    # Log
    log.info("No flattening required, leaving unchanged")

    # Return
    return path
