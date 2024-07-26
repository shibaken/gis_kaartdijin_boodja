"""Kaartdijin Boodja Publisher GeoServer Queue Excutor."""

# Standard
import logging

# Third-Party
from django.db.models import Q
from django.utils import timezone
from django.contrib import auth

# Local
from govapp.apps.publisher.models import geoserver_queues
from govapp.apps.publisher.models import geoserver_roles_groups
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueueStatus
from govapp.apps.publisher.models import geoserver_pools
from govapp.apps.publisher import geoserver_publisher
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerRole
from govapp.apps.publisher.models.publish_channels import GeoServerPublishChannel
from govapp.apps.publisher.models.workspaces import Workspace
from govapp.gis import geoserver

# Typing
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from govapp.apps.publisher.models.publish_entries import PublishEntry
    
# Shortcuts
UserModel = auth.get_user_model()
# Logging
log = logging.getLogger(__name__)

QUEUE_EXPIRED_MINUTES = 1

class GeoServerQueueExcutor:
    def __init__(self) -> None:
        self.result_status = GeoServerQueueStatus.PUBLISHED
        self.result_success = True
        self.publishing_log = ""

    def excute(self) -> None:
        target_items = self._retrieve_target_items()
        log.info(f"Start publishing for {target_items.count()} geoserver queue items.")

        for queue_item in target_items:
            self._init_excuting(queue_item=queue_item)
        
            for geoserver_publish_channel in queue_item.publish_entry.geoserver_channels.all():
                geoserver_pool = geoserver_publish_channel.geoserver_pool
                if geoserver_pool.enabled:
                    # Make sure all the workspace exist in the geoserver
                    workspaces_in_kb = Workspace.objects.all()
                    for workspace in workspaces_in_kb:
                        # geoserver_obj.create_workspace_if_not_exists(workspace.name)
                        geoserver_pool.create_workspace_if_not_exists(workspace.name)

                    self._publish_to_a_geoserver(publish_entry=queue_item.publish_entry, geoserver_info=geoserver_publish_channel)

            self._update_result(queue_item=queue_item)

    def _retrieve_target_items(self):
        """ Retrieve items that their status is ready or status is on_publishing & started before 30 minutes from now """
        query = Q(status=GeoServerQueueStatus.READY) | \
                Q(status=GeoServerQueueStatus.ON_PUBLISHING, started_at__lte=timezone.now() - timezone.timedelta(minutes=QUEUE_EXPIRED_MINUTES))
        
        return geoserver_queues.GeoServerQueue.objects.filter(query)
    
    def _init_excuting(self, queue_item):
        queue_item.change_status(GeoServerQueueStatus.ON_PUBLISHING)
        self.publishing_log = queue_item.publishing_result if queue_item.publishing_result is not None else ""
        self.result_status = GeoServerQueueStatus.PUBLISHED
        self._add_publishing_log("Start publishing..")

    def _add_publishing_log(self, msg):
        log.info(msg)
        log_msg = f"[{timezone.now()}] {msg}\n"
        # log.info(log_msg)
        self.publishing_log += log_msg
        return log_msg
    
        
    def _publish_to_a_geoserver(self, publish_entry: "PublishEntry", geoserver_info: GeoServerPublishChannel):
        geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_info.geoserver_pool.url, geoserver_info.geoserver_pool.username, geoserver_info.geoserver_pool.password)
        
        # Publish here
        res, exc = geoserver_publisher.publish(publish_entry, geoserver_obj, geoserver_info)
        
        if res:
            self._add_publishing_log(f"[{publish_entry.name} - {geoserver_info.geoserver_pool.url}] Publishing succeed.")
            
        else :
            self.result_status = GeoServerQueueStatus.FAILED
            self.result_success = False
            self._add_publishing_log(f"[{publish_entry.name} - {geoserver_info.geoserver_pool.url}] Publishing failed.")
            self._add_publishing_log(f"[{publish_entry.name} - {geoserver_info.geoserver_pool.url}] {exc}")
            
    def _update_result(self, queue_item: geoserver_queues.GeoServerQueue):
        queue_item.status = self.result_status
        queue_item.success = self.result_success
        queue_item.publishing_result = self.publishing_log
        queue_item.save()
    
def push(publish_entry: "PublishEntry", symbology_only: bool, submitter: UserModel=None) -> bool:
    if not hasattr(publish_entry, "geoserver_channels"):
        log.info(f"'{publish_entry}' has no GeoServer Publish Channel")
        return False
    
    geoserver_queues.GeoServerQueue.objects.create(
        publish_entry=publish_entry,
        symbology_only=symbology_only,
        submitter=submitter)
    return True


class GeoServerSyncExcutor:
    def sync_geoserver_roles(self):
        log.info(f"Sync geoserver roles...")
        
        # List of the active role names in the KB
        geoserver_role_names = GeoServerRole.objects.filter(active=True).values_list('name', flat=True)
        log.info(f'Roles in KB: [{geoserver_role_names}]')

        # List of the active geoservers in the KB
        geoserver_pool = geoserver_pools.GeoServerPool.objects.filter(enabled=True)

        for geoserver_info in geoserver_pool:  # Perform per geoserver
            geoserver_info.synchronize_roles(geoserver_role_names)

    def sync_geoserver_groups(self):
        log.info(f"Sync geoserver groups...")
        
        # List of the active group names in the KB
        geoserver_group_names = GeoServerGroup.objects.filter(active=True).values_list('name', flat=True)
        log.info(f'Groups in KB: [{geoserver_group_names}]')

        # List of the active geoservers in the KB
        geoserver_pool = geoserver_pools.GeoServerPool.objects.filter(enabled=True)

        for geoserver_info in geoserver_pool:  # Perform per geoserver
            geoserver_info.synchronize_groups(geoserver_group_names)

    def sync_geoserver_role_permissions(self):
        log.info(f"Sync geoserver rules...")

        # List of the active geoservers in the KB
        geoserver_pool = geoserver_pools.GeoServerPool.objects.filter(enabled=True)
        new_rules = geoserver_roles_groups.GeoServerRolePermission.get_rules()
        workspaces_in_kb = set(list(Workspace.objects.all().values_list('name', flat=True)))

        for geoserver_info in geoserver_pool:  # Perform per geoserver
            # Generate GeoServer obj
            # geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_info.url, geoserver_info.username, geoserver_info.password)
            
            # Make sure all the workspace exist in the geoserver
            for workspace in workspaces_in_kb:
                geoserver_info.create_workspace_if_not_exists(workspace)
            geoserver_info.synchronize_rules(new_rules)

            workspaces_in_geoserver = geoserver_info.get_all_workspaces()
            workspaces_in_geoserver = set([workspace['name'] for workspace in workspaces_in_geoserver])
            log.info(f'Workspaces: [{workspaces_in_geoserver}] exist in the geoserver: [{geoserver_info}].')

            workspaces_to_be_deleted = workspaces_in_geoserver - workspaces_in_kb
            for workspace_to_be_deleted in workspaces_to_be_deleted:
                geoserver_info.delete_workspace(workspace_to_be_deleted)


    def sync_deleted_layers(self):
        log.info(f"Remove all layers on Geoservers that have been removed from KB...")
        
        geoserver_pool = geoserver_pools.GeoServerPool.objects.filter(enabled=True)
        for geoserver_info in geoserver_pool:
            geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_info.url, geoserver_info.username, geoserver_info.password)
            
            # Retrive layer names from geoserver
            layers = geoserver_obj.get_layers()
            layer_names = [layer['name'].split(':')[1] for layer in layers]

            log.info(f'Layers on the geoserver: [{geoserver_info.url}: [{layer_names}]]')
            
            # Retrive layer names from DB for this geoserver
            name_list = GeoServerPublishChannel.objects.filter(
                geoserver_pool=geoserver_info,
                publish_entry__catalogue_entry__name__in=[layer_name for layer_name in layer_names]
            ).values_list('publish_entry__catalogue_entry__name', flat=True)
            synced_layer_names_set = set(name_list)

            log.info(f'Layers on the KB: [{synced_layer_names_set}] for the geoserver: [{geoserver_info.url}]')
            
            # Compare layer names
            purge_list = [layer_name for layer_name in layer_names if layer_name not in synced_layer_names_set]

            log.info(f'Layers to be deleted: [{purge_list}] from the geoserver: [{geoserver_info.url}]')
            
            # Call a remove layer api
            for purge in purge_list:
                geoserver_obj.delete_layer(purge)
