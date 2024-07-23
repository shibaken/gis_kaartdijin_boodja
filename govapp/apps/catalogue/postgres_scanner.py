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
        log.info("Scanning Postgres Queries...")
        days_of_week = {
            1 : "Mon",
            2 : "Tue",
            3 : "Wed",
            4 : "Thu",
            5 : "Fri",
            6 : "Sat",
            7 : "Sun"
        }
        catalogue_entry_list = catalogue_entries.CatalogueEntry.objects.filter(
            type=catalogue_entries.CatalogueEntryType.SUBSCRIPTION_QUERY,
            layer_subscription__status=layer_subscriptions.LayerSubscriptionStatus.LOCKED
        )
        log.debug(f'[{catalogue_entry_list}]')
        for catalogue_entry_obj in catalogue_entry_list:
            cqf = custom_query_frequency.CustomQueryFrequency.objects.filter(catalogue_entry=catalogue_entry_obj)
            for custom_query_freq in cqf:
                is_time_to_run = False
                generate_shp = False
                now_dt = datetime.now(tz=ZoneInfo(conf.settings.TIME_ZONE))
                
                print (custom_query_freq.catalogue_entry.name)

                # Every minute scheduler.
                if custom_query_freq.type == custom_query_frequency.FrequencyType.EVERY_MINUTES:
                    if custom_query_freq.last_job_run is None:
                        is_time_to_run = True
                    else:
                        dt_diff = now_dt - custom_query_freq.last_job_run.astimezone()
                        last_job_run_in_minutes = dt_diff.total_seconds() / 60
                        print (last_job_run_in_minutes)
                        if last_job_run_in_minutes > custom_query_freq.every_minutes:
                            is_time_to_run = True

                    if is_time_to_run is True:
                        generate_shp = True
                # Every hour scheduler.
                elif custom_query_freq.type == custom_query_frequency.FrequencyType.EVERY_HOURS:
                    if custom_query_freq.last_job_run is None:
                        is_time_to_run = True
                    else:
                        dt_diff = now_dt - custom_query_freq.last_job_run.astimezone()
                        last_job_run_in_hours = dt_diff.total_seconds() / 60 / 60
                        if last_job_run_in_hours >= custom_query_freq.every_hours:
                            is_time_to_run = True
                    if is_time_to_run is True:
                        generate_shp = True
                # Daily scheduler.
                elif custom_query_freq.type == custom_query_frequency.FrequencyType.DAILY:
                    if custom_query_freq.last_job_run is None:
                        is_time_to_run = True
                    else:
                        now_dt_string = now_dt.strftime("%Y-%m-%d")
                        last_job_run_string = custom_query_freq.last_job_run.strftime("%Y-%m-%d")
                        if now_dt_string == last_job_run_string:
                            is_time_to_run = False
                        else:
                            is_time_to_run = True

                    if is_time_to_run is True:
                        if now_dt.hour >= custom_query_freq.hour or now_dt.hour == custom_query_freq.hour:
                            if now_dt.hour == custom_query_freq.hour:
                                if now_dt.minute >= custom_query_freq.minute or now_dt.minute == custom_query_freq.minute:
                                    generate_shp = True
                            else:
                                generate_shp = True
                         

                    else:
                        print ("Job not requried to run.")
                # Weekly scedhuler
                elif custom_query_freq.type == custom_query_frequency.FrequencyType.WEEKLY:
                    if custom_query_freq.last_job_run is None:
                        is_time_to_run = True
                    else:
                        last_job_run_string = custom_query_freq.last_job_run.strftime("%Y-%m-%d")
                        last_job_run_string_dow = custom_query_freq.last_job_run.strftime("%a")
                        now_dt_string_dow = now_dt.strftime("%a")

                        print (now_dt_string_dow)
                        print (last_job_run_string_dow)
                        
                        if now_dt_string_dow == last_job_run_string_dow:
                            is_time_to_run = False
                        else:
                            if custom_query_freq.day_of_week > 0:
                                if days_of_week[custom_query_freq.day_of_week] == now_dt_string_dow:
                                    if now_dt.hour >= custom_query_freq.hour or now_dt.hour == custom_query_freq.hour:
                                        if now_dt.hour == custom_query_freq.hour:
                                            if now_dt.minute >= custom_query_freq.minute or now_dt.minute == custom_query_freq.minute:
                                                is_time_to_run = True
                                        else:
                                            is_time_to_run = True

                    if is_time_to_run is True:
                        generate_shp = True
                # Monthly Schedule
                elif custom_query_freq.type == custom_query_frequency.FrequencyType.MONTHLY:  
                    if custom_query_freq.last_job_run is None:
                        is_time_to_run = True
                    else:                
                        now_dt_string = now_dt.strftime("%Y-%m-%d")
                        last_job_run_string = custom_query_freq.last_job_run.strftime("%Y-%m-%d")       
                        now_dt_string_dom = now_dt.strftime("%-d")
                        last_job_run_string_dom = custom_query_freq.last_job_run.strftime("%-d")

                        if now_dt_string == last_job_run_string:
                            is_time_to_run = False
                        else:
                            if int(now_dt_string_dom) >= int(last_job_run_string_dom):
                                    if now_dt.hour >= custom_query_freq.hour or now_dt.hour == custom_query_freq.hour:
                                        if now_dt.hour == custom_query_freq.hour:
                                            if now_dt.minute >= custom_query_freq.minute or now_dt.minute == custom_query_freq.minute:
                                                is_time_to_run = True   
                                        else:
                                            is_time_to_run = True                       

                            if is_time_to_run is True:
                                generate_shp = True
                if generate_shp is True:  
                    try:
                        co = conversions.postgres_to_shapefile(
                            catalogue_entry_obj.name,
                            catalogue_entry_obj.layer_subscription.host,
                            catalogue_entry_obj.layer_subscription.username,
                            catalogue_entry_obj.layer_subscription.userpassword,
                            catalogue_entry_obj.layer_subscription.database,
                            catalogue_entry_obj.layer_subscription.port,
                            catalogue_entry_obj.sql_query
                        )
                        new_path = shutil.move(co["compressed_filepath"], conf.settings.PENDING_IMPORT_PATH)
                        log.info(f'CatalogueEntry: [{catalogue_entry_obj}] has been converted to the shapefile: [{new_path}].')
                    except Exception as e:
                        log.error(f"ERROR Running POSTGIS to Shapefile conversation for the CatalogueEntry: [{catalogue_entry_obj}]")
                    
                    custom_query_freq.last_job_run = now_dt
                    custom_query_freq.save()
                    

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
