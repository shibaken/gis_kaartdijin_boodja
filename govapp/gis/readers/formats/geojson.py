"""GeoJSON GIS Reader."""


# Standard
import pathlib
import logging
import json

from govapp.gis import utils

# Local
from govapp.gis.readers import base
from govapp.gis.readers.types import Metadata

# Logging
logger = logging.getLogger(__name__)


class GeoJSONReader(base.LayerReader):
    """GeoJSON Layer Reader."""

    @classmethod
    def is_compatible(cls, file: pathlib.Path) -> bool:
        """Determines whether this file is a GeoJSON file.

        Args:
            file (pathlib.Path): Path to the file to check.

        Returns:
            bool: Whether this file is compatible with this reader.
        """
        # Check and Return
        # if file.is_file() and file.suffix.lower() in (".json", ".geojson"):
        #     return True
        if file.is_dir() and utils.exists(file.glob("*.json")) or file.is_dir() and utils.exists(file.glob("*.geojson")):
            if cls.geojson_has_name_property(file):
                return True
        return False
        
    @classmethod
    def geojson_has_name_property(cls, path_to_folder):
        """Determines whether the GeoJSON file has a name property."""
        if cls.contain_single_geojson(path_to_folder):
            geojson_files = cls.get_geojson_files(path_to_folder)
            with open(geojson_files[0]) as f:
                data = json.load(f)
                if 'name' in data:
                    return True
                logger.error(f'The GeoJSON file does not have a name property at the top level: [{geojson_files[0]}]')
                raise ValueError(f'The GeoJSON file does not have a name property at the top level: [{geojson_files[0]}]')
        logger.error(f'There are more than one GeoJSON files in the folder: [{path_to_folder}]')
        raise ValueError(f'There are more than one GeoJSON files in the folder: [{path_to_folder}]')

    @classmethod
    def contain_single_geojson(cls, path_to_folder):
        """Determines whether the folder contains only one GeoJSON file."""
        return len(cls.get_geojson_files(path_to_folder)) == 1    
    
    @classmethod
    def get_geojson_files(cls, path_to_folder):
        """Returns a list of GeoJSON files in a folder."""
        json_files = list(path_to_folder.glob("*.json"))
        geojson_files = list(path_to_folder.glob("*.geojson"))
        return json_files + geojson_files
