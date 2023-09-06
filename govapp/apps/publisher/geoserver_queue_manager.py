"""Kaartdijin Boodja Publisher GeoServer Queue Excutor."""

# Standard
import logging

# Third-Party
from django.db.models import Q
from django.utils import timezone

# Local
from govapp.apps.publisher.models import geoserver_queues
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueueStatus
from govapp.apps.publisher.models import geoserver_pools
from govapp.apps.publisher import geoserver_publisher
from govapp.gis import geoserver

# Typing
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from govapp.apps.publisher.models.publish_entries import PublishEntry
    
# Logging
log = logging.getLogger(__name__)

QUEUE_EXPIRED_MINUTES = 1
 
def excute():
    target_items = _retrieve_target_items()
    log.info(f"Start publishing for {target_items.count()} geoserver queue items.")
    for queue_item in target_items:
        queue_item.change_status(GeoServerQueueStatus.ON_PUBLISHING)
        publishing_log = queue_item.publishing_result if queue_item.publishing_result is not None else ""
        publishing_log += _publishing_log("Start publishg..")
        result_status = GeoServerQueueStatus.PUBLISHED
        
        # Retrieving information of all eabled geoserver from the pool
        geoserver_pool = geoserver_pools.GeoServerPool.objects.filter(enabled=True)
        
        for geoserver_info in geoserver_pool:
            geoserver_obj = geoserver.geoserverWithCustomCreds(
                geoserver_info.url, geoserver_info.username, geoserver_info.password)
            
            # Publish here
            res, exc = geoserver_publisher.publish(queue_item.publish_entry, geoserver_obj)
            
            if res:
                publishing_log += _publishing_log(f"[{queue_item.publish_entry.name} - {geoserver_info.url}] Publishing succeed.")
                
            else :
                result_status = GeoServerQueueStatus.FAILED
                publishing_log += _publishing_log(f"[{queue_item.publish_entry.name} - {geoserver_info.url}] Publishing failed.")
                publishing_log += _publishing_log(f"[{queue_item.publish_entry.name} - {geoserver_info.url}] {exc}")
            
        queue_item.status = result_status
        queue_item.publishing_result = publishing_log
        queue_item.save()
    return

def push(publish_entry: "PublishEntry", symbology_only: bool) -> bool:
    if not hasattr(publish_entry, "geoserver_channel"):
        log.info(f"'{publish_entry}' has no GeoServer Publish Channel")
        return False
    
    geoserver_queues.GeoServerQueue.objects.create(
        publish_entry=publish_entry,
        symbology_only=symbology_only)
    return True

def _retrieve_target_items():
    """ Retrieve items that their status is ready or status is on_publishing & started before 30 minutes from now """
    query = Q(status=GeoServerQueueStatus.READY) | \
            Q(status=GeoServerQueueStatus.ON_PUBLISHING, started_at__lte=timezone.now() - timezone.timedelta(minutes=QUEUE_EXPIRED_MINUTES))
    
    return geoserver_queues.GeoServerQueue.objects.filter(query)

def _publishing_log(msg):
    log_msg = f"[{timezone.now()}] {msg}\n"
    log.info(log_msg)
    return log_msg
    