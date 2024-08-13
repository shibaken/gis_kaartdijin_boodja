"""Kaartdijin Boodja Catalogue Django Application Scanner."""

# Standard
import logging
import shutil
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

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
    def __init__(self) -> None:
        """Instantiates the Scanner."""
        # Storage        
        #self.storage = local_storage.LocalStorage()

    def scan(self) -> None:
        # Log
        log.info("Start scanning postgres queries...")
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
        )

        for catalogue_entry_obj in catalogue_entry_list:
            log.info(f'Scanning postgres queries for the CatalogueEntry: [{catalogue_entry_obj}]...')

            if catalogue_entry_obj.layer_subscription.status != layer_subscriptions.LayerSubscriptionStatus.LOCKED:
                log.warn(f'CatalogueEntry: [{catalogue_entry_obj}] is skipped to process because its layer_subscription is not LOCKED.')
                continue

            for custom_query_freq in catalogue_entry_obj.custom_query_frequencies.all():  # CatalogueEntry can have 0 or 1 custom_query_frequency.
                log.info(f'Working on the CustomQueryFrequency: [{catalogue_entry_obj}] for the CatalogueEntry: [{catalogue_entry_obj}]...')
                is_time_to_run = False
                generate_shp = False
                now_dt = datetime.now(tz=ZoneInfo(conf.settings.TIME_ZONE))
                log.info(f'Now datetime is [{now_dt}].')

                if catalogue_entry_obj.force_run_postgres_scanner:
                    # When force_run_postgres_scanner is set to True, we don't need to check the schedule
                    generate_shp = True
                else:
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
                        log.info(f'CustomQueryFrequency: [{custom_query_freq}] type is DAILY.')
                        if custom_query_freq.last_job_run is None:
                            is_time_to_run = True
                            log.info(f'is_time_to_run is set to True for the CustomQueryFrequency: [{custom_query_freq}] because it has never been run.')
                        else:
                            now_dt_string = now_dt.strftime("%Y-%m-%d")
                            # last_job_run_string = custom_query_freq.last_job_run.strftime("%Y-%m-%d")
                            last_job_run = custom_query_freq.last_job_run.astimezone(ZoneInfo(conf.settings.TIME_ZONE))
                            last_job_run_string = last_job_run.strftime("%Y-%m-%d")
                            if now_dt_string != last_job_run_string:
                                is_time_to_run = True
                                log.info(f'is_time_to_run is set to True for the CustomQueryFrequency: [{custom_query_freq}] because now_dt_string: [{now_dt_string}] is not same as the last_job_run_string: [{last_job_run_string}].')
                            else:
                                log.info(f'is_time_to_run remains False because now_dt_string: [{now_dt_string}] is the same as the last_job_run_string: [{last_job_run_string}].')

                        if is_time_to_run:
                            # Check if the current time has passed the specified time in a single condition
                            if (now_dt.hour, now_dt.minute) >= (custom_query_freq.hour, custom_query_freq.minute):
                                log.info(f'The time of now_dt has passed the one of the custom_query_freq.  Set True to the generate_shp.')
                                generate_shp = True
                            else:
                                log.info(f'Since the current time (now_dt): [{now_dt}] has not yet been reached the time of the custom_query_freq: [{custom_query_freq}], generate_shp remains False.')
                        else:
                            log.info("Conversion not requried to run.")

                    # Weekly scedhuler
                    elif custom_query_freq.type == custom_query_frequency.FrequencyType.WEEKLY:
                        if custom_query_freq.last_job_run is None:
                            is_time_to_run = True
                        else:
                            # last_job_run_string = custom_query_freq.last_job_run.strftime("%Y-%m-%d")
                            # last_job_run_string_dow = custom_query_freq.last_job_run.strftime("%a")
                            last_job_run = custom_query_freq.last_job_run.astimezone(ZoneInfo(conf.settings.TIME_ZONE))
                            last_job_run_string = last_job_run.strftime("%Y-%m-%d")
                            last_job_run_string_dow = last_job_run.strftime("%a")
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
                        generate_shp = Scanner.should_process_monthly(now_dt, custom_query_freq)

                if generate_shp:  
                    Scanner.run_postgres_to_shapefile(catalogue_entry_obj, custom_query_freq, now_dt)
                    catalogue_entry_obj.force_run_postgres_scanner = False
                    catalogue_entry_obj.save()

        # Log
        log.info("Scanning storage staging area complete!")
    
    @staticmethod
    def should_process_monthly(now, custom_query_freq):
        if not custom_query_freq.last_job_run:
            # Scanning has never been run so far.  --> Run job
            log.info(f'CatalogueEntry: [{custom_query_freq.catalogue_entry}] has never been scanned for custom query.  Run scanning.')
            return True

        # Align timezone
        last_job_run = custom_query_freq.last_job_run.astimezone(ZoneInfo(conf.settings.TIME_ZONE))

        next_job_run = last_job_run + relativedelta(months=1)
        if next_job_run < now:
            # Somehow, the last job has been run before one month ago from now
            log.info(f'The last job run: [{last_job_run}] is somehow more than one monthe before now: [{now}].  Run scanning.')
            return True

        # Calculate the scheduled time for the current month
        try:
            scheduled_time = now.replace(day=custom_query_freq.date, hour=custom_query_freq.hour, minute=custom_query_freq.minute, second=0, microsecond=0)
        except ValueError:
            # For invalid dates (e.g., February 30th), use the last day of the month
            last_day = calendar.monthrange(now.year, now.month)[1]
            scheduled_time = now.replace(day=last_day, hour=custom_query_freq.hour, minute=custom_query_freq.minute, second=0, microsecond=0)

        if last_job_run < scheduled_time:
            if scheduled_time <= now:
                # Scheduled run datetime is after the last job run datetime, and It's before now. ==> Run the job
                log.info(f'The last job run datetime: [{last_job_run}] is before the scheduled datetime: [{scheduled_time}] and it is before now: [{now}].  Run scanning.')
                return True
            else:
                log.info(f'The last job run datetime: [{last_job_run}] is before the scheduled datetime: [{scheduled_time}] but the scheduled datetime is after now: [{now}].  Do not run scanning.')
                return False
        else:
            log.info(f'The last job run datetime: [{last_job_run}] is after the scheduled datetime: [{scheduled_time}].  Do not run scanning.')
            return False
    
    @staticmethod
    def run_postgres_to_shapefile(catalogue_entry_obj, custom_query_freq=None, now_dt=datetime.now(tz=ZoneInfo(conf.settings.TIME_ZONE))):
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
            log.error(f"ERROR Running POSTGIS to Shapefile conversation for the CatalogueEntry: [{catalogue_entry_obj}]. error: [{e}]")
            raise

        if custom_query_freq:
            custom_query_freq.last_job_run = now_dt
            custom_query_freq.save()
        else:
            catalogue_entry_obj.custom_query_frequencies.update(last_job_run=now_dt)
        return new_path

