"""Kaartdijin Boodja Catalogue Django Application Scanner."""

# Standard
import logging
import os 
import shutil
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

# Third-Party
from django import conf

# Local
from govapp.apps.catalogue.models import layer_subscriptions
from govapp.apps.catalogue.models import catalogue_entries
from govapp.apps.catalogue.models import custom_query_frequency
from govapp.gis import conversions
from django import conf
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
        days_of_week = {
                1 : "Mon",
                2 : "Tue",
                3 : "Wed",
                4 : "Thu",
                5 : "Fri",
                6 : "Sat",
                7 : "Sun"

        }

        #lay_sub = layer_subscriptions.LayerSubscription.objects.filter(type=3)
        cat_ent = catalogue_entries.CatalogueEntry.objects.filter(type=5, layer_subscription__status=2)
        for ce in cat_ent:
            
            cqf = custom_query_frequency.CustomQueryFrequency.objects.filter(catalogue_entry=ce)
            for row in cqf:
                is_time_to_run = False
                generate_shp = False
                now_dt = datetime.now(tz=ZoneInfo(conf.settings.TIME_ZONE))
                
                print (row.catalogue_entry.name)

                # Every minute scheduler.
                if row.type == 1:
                    if row.last_job_run is None:
                        is_time_to_run = True
                    else:
                        dt_diff = now_dt - row.last_job_run.astimezone()
                        last_job_run_in_minutes = dt_diff.total_seconds() / 60
                        print (last_job_run_in_minutes)
                        if last_job_run_in_minutes > row.every_minutes:
                            is_time_to_run = True

                    if is_time_to_run is True:
                        generate_shp = True
                    

                # Every hour scheduler.
                elif row.type == 2:
                    if row.last_job_run is None:
                        is_time_to_run = True
                    else:
                        dt_diff = now_dt - row.last_job_run.astimezone()
                        last_job_run_in_hours = dt_diff.total_seconds() / 60 / 60
                        if last_job_run_in_hours >= row.every_hours:
                            is_time_to_run = True
                    if is_time_to_run is True:
                        generate_shp = True

                # Daily scheduler.
                elif row.type == 3:
                    if row.last_job_run is None:
                        is_time_to_run = True
                    else:
                        now_dt_string = now_dt.strftime("%Y-%m-%d")
                        last_job_run_string = row.last_job_run.strftime("%Y-%m-%d")
                        if now_dt_string == last_job_run_string:
                            is_time_to_run = False
                        else:
                            is_time_to_run = True

                    if is_time_to_run is True:
                        if now_dt.hour >= row.hour or now_dt.hour == row.hour:
                            if now_dt.hour == row.hour:
                                if now_dt.minute >= row.minute or now_dt.minute == row.minute:
                                    generate_shp = True
                            else:
                                generate_shp = True
                         

                    else:
                        print ("Job not requried to run.")
                # Weekly scedhuler
                elif row.type == 4:
                    if row.last_job_run is None:
                        is_time_to_run = True
                    else:
                        last_job_run_string = row.last_job_run.strftime("%Y-%m-%d")
                        last_job_run_string_dow = row.last_job_run.strftime("%a")
                        now_dt_string_dow = now_dt.strftime("%a")

                        print (now_dt_string_dow)
                        print (last_job_run_string_dow)
                        
                        if now_dt_string_dow == last_job_run_string_dow:
                            is_time_to_run = False
                        else:
                            if row.day_of_week > 0:
                                if days_of_week[row.day_of_week] == now_dt_string_dow:
                                    if now_dt.hour >= row.hour or now_dt.hour == row.hour:
                                        if now_dt.hour == row.hour:
                                            if now_dt.minute >= row.minute or now_dt.minute == row.minute:
                                                is_time_to_run = True
                                        else:
                                            is_time_to_run = True

                    if is_time_to_run is True:
                        generate_shp = True
                
                # Monthly Schedule
                elif row.type == 5:  
                    if row.last_job_run is None:
                        is_time_to_run = True
                    else:                
                        now_dt_string = now_dt.strftime("%Y-%m-%d")
                        last_job_run_string = row.last_job_run.strftime("%Y-%m-%d")       
                        now_dt_string_dom = now_dt.strftime("%-d")
                        last_job_run_string_dom = row.last_job_run.strftime("%-d")

                        if now_dt_string == last_job_run_string:
                            is_time_to_run = False
                        else:
                            if int(now_dt_string_dom) >= int(last_job_run_string_dom):
                                    if now_dt.hour >= row.hour or now_dt.hour == row.hour:
                                        if now_dt.hour == row.hour:
                                            if now_dt.minute >= row.minute or now_dt.minute == row.minute:
                                                is_time_to_run = True   
                                        else:
                                            is_time_to_run = True                       

                            if is_time_to_run is True:
                                generate_shp = True
                if generate_shp is True:  
                    try:
                        co = conversions.postgres_to_shapefile(ce.name,ce.layer_subscription.host,ce.layer_subscription.username,ce.layer_subscription.userpassword,ce.layer_subscription.database,ce.layer_subscription.port,ce.sql_query)
                        shutil.move(co["compressed_filepath"],conf.settings.PENDING_IMPORT_PATH)
                    except Exception as e:
                        print ("ERROR Running POSTGIS to Shapefile conversation")
                        print (e)
                    
                    row.last_job_run = now_dt
                    row.save()
                    

                        #row.last_job_run = datetime.now()
                        #row.save()


                        
                    

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
