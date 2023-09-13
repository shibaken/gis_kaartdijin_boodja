"""Kaartdijin Boodja Catalogue Django Application Scanner."""

# Standard
import logging
import os 

# Third-Party
from django import conf

# Local
from govapp.apps.catalogue.models import layer_subscriptions
from govapp.apps.catalogue.models import catalogue_entries
from govapp.gis import conversions
# from govapp.common import local_storage
# from govapp.apps.catalogue import directory_absorber
# from govapp.apps.catalogue import notifications


# Logging
log = logging.getLogger(__name__)


class Scanner:
    """Scans for files to be absorbed into the system."""

    def __init__(self) -> None:
        """Instantiates the Scanner."""
        # Storage        
        #self.storage = local_storage.LocalStorage()

    def scan(self) -> None:
        """Scans for new files in the staging area to be absorbed."""
        # Log
        log.info("Scanning Postgres Queries")
        #lay_sub = layer_subscriptions.LayerSubscription.objects.filter(type=3)
        cat_ent = catalogue_entries.CatalogueEntry.objects.filter(layer_subscription__type=3)
        print ("RUNN")
        print (cat_ent)
        for ce in cat_ent:           
            print (ce.layer_subscription.host)
            print (ce.layer_subscription.port)
            print (ce.layer_subscription.username)
            print (ce.layer_subscription.userpassword)
            print (ce.sql_query)
            conversions.postgres_to_shapefile(ce.name,ce.layer_subscription.host,ce.layer_subscription.username,ce.layer_subscription.userpassword,ce.layer_subscription.database,ce.layer_subscription.port,ce.sql_query)
        # Retrieve file from remote storage staging area
    

        #files_array = os.listdir(self.storage.get_pending_import_path())

        #print (files_array)


        # files = self.storage.list(conf.settings.SHAREPOINT_INPUT_STAGING_AREA)

        # Check for files
        #if not files_array:
        #     # Log
        #     log.info("No files found")

        # # Loop through files
        # for file in files_array:
        #     # Log
        #     log.info(f"Discovered file '{file}'")

        #     # Handle errors
        #     # For example, if someone drops in a malformed file or a non-GIS file
        #     try:
        #         # Absorb!
        #         directory_absorber.Absorber().absorb(file)

        #     except Exception as exc:
        #         # Log and continue
        #         log.error(f"Error absorbing file '{file}': {exc}")

        #         # Notify!                
        #         #notifications.file_absorb_failure(file)

        # Log
        log.info("Scanning storage staging area complete!")
