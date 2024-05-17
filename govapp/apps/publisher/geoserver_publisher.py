"""Kaartdijin Boodja Publisher GeoServer Queue Excutor."""

# Standard
import logging

# Third-Party

# Local
from govapp.apps.publisher import notifications as notifications_utils
from govapp.gis import geoserver
from govapp.apps.catalogue.models import layer_subscriptions
from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntryType
from govapp.apps.publisher.models.publish_channels import GeoServerPublishChannel

# Typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from govapp.apps.publisher.models.publish_entries import PublishEntry
    from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntry

# Logging
log = logging.getLogger(__name__)

# """Publish to GeoServers."""
def publish(publish_entry: "PublishEntry", geoserver:geoserver.GeoServer, geoserver_info:GeoServerPublishChannel , symbology_only: bool = False) -> (bool, Exception):
    """Publishes to GeoServer channel if applicable.

    Args:
        symbology_only (bool): Flag to only publish symbology.
    """
    # Check for Publish Channel
    if not hasattr(publish_entry, "geoserver_channels"):
        # Log
        log.info(f"'{publish_entry}' has no GeoServer1 Publish Channel")

        # Exit Early
        return

    # Log
    log.info(f"Publishing '{publish_entry.catalogue_entry}' - '{publish_entry.geoserver_channels}' ({symbology_only=})")

    # Handle Errors
    try:
        ### Publish! ###
        # Make sure workspace exists
        geoserver.create_workspace_if_not_exists(geoserver_info.workspace.name)
        # for special file
        if publish_entry.catalogue_entry.type in [CatalogueEntryType.SPATIAL_FILE, CatalogueEntryType.SUBSCRIPTION_QUERY]:
            geoserver_info.publish(symbology_only, geoserver)
        # for layer subscription
        else:
            _publish(publish_entry, geoserver, geoserver_info)

    except Exception as exc:
        # Log
        log.error(f"Unable to publish to GeoServer Publish Channel: {exc}")

        # Send Failure Emails
        notifications_utils.publish_entry_publish_failure(publish_entry)
        
        return False, exc

    else:
        # Send Success Emails
        notifications_utils.publish_entry_publish_success(publish_entry)
        
    return True, None

def _publish(publish_entry: "PublishEntry", geoserver:geoserver.GeoServer, geoserver_info:GeoServerPublishChannel):
    catalogue_entry = publish_entry.catalogue_entry
    layer_subscription = catalogue_entry.layer_subscription
    
    if layer_subscription.type == layer_subscriptions.LayerSubscriptionType.WFS:
        _publish_wfs(publish_entry, catalogue_entry, layer_subscription, geoserver, geoserver_info)
    elif layer_subscription.type == layer_subscriptions.LayerSubscriptionType.WMS:
        _publish_wms(publish_entry, catalogue_entry, layer_subscription, geoserver, geoserver_info)
    elif layer_subscription.type == layer_subscriptions.LayerSubscriptionType.POST_GIS:
        _publish_postgis(publish_entry, catalogue_entry, layer_subscription, geoserver, geoserver_info)

def _publish_wfs(
        publish_entry: "PublishEntry", 
        catalogue_entry: "CatalogueEntry", 
        layer_subscription: "layer_subscriptions.LayerSubscription",
        geoserver:geoserver.GeoServer,
        geoserver_info:GeoServerPublishChannel
    ):
    context = {
      "name": layer_subscription.name,
      "description": layer_subscription.description,
      "enabled": layer_subscription.enabled,
      "capability_url": layer_subscription.url,
      "username": layer_subscription.username,
      "password": layer_subscription.userpassword,
    }
    geoserver.upload_store_wfs(workspace=layer_subscription.workspace, store_name=layer_subscription.name, context=context)

    context = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description,
        "native_name":catalogue_entry.mapping_name,
        "title":catalogue_entry.name,
        "abstract": None,
        "override_bbox": geoserver_info.override_bbox,
        "native_crs":geoserver_info.native_crs,
        "crs": geoserver_info.srs,
        "nativeBoundingBox": {
            "minx": geoserver_info.nbb_minx,
            "maxx": geoserver_info.nbb_maxx,
            "miny": geoserver_info.nbb_miny,
            "maxy": geoserver_info.nbb_maxy,
            "crs": geoserver_info.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_info.llb_minx,
            "maxx": geoserver_info.llb_maxx,
            "miny": geoserver_info.llb_miny,
            "maxy": geoserver_info.llb_maxy,
            "crs": geoserver_info.llb_crs,
        },
        "enabled": "true",
        # "keywords":, #?
    }
    geoserver.upload_layer_wfs(workspace=layer_subscription.workspace.name, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context)
    
def _publish_wms(
        publish_entry: "PublishEntry", 
        catalogue_entry: "CatalogueEntry", 
        layer_subscription: "layer_subscriptions.LayerSubscription",
        geoserver:geoserver.GeoServer,
        geoserver_info:GeoServerPublishChannel
    ):
    context = {
      "name": layer_subscription.name,
      "description": layer_subscription.description,
      "enabled": layer_subscription.enabled,
      "capability_url": layer_subscription.url,
      "username": layer_subscription.username,
      "password": layer_subscription.userpassword,
      "geoserver_setting": {
          "max_connections": layer_subscription.max_connections,
          "read_timeout": layer_subscription.read_timeout,
          "connect_timeout": layer_subscription.connection_timeout,
      }
    }
    geoserver.upload_store_wms(workspace=layer_subscription.workspace, store_name=layer_subscription.name, context=context)
    
    context = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description,
        "native_name": catalogue_entry.mapping_name,
        "title": catalogue_entry.name,
        "abstract": None,
        "override_bbox": geoserver_info.override_bbox,
        "native_crs": geoserver_info.native_crs,
        "crs": geoserver_info.srs,
        "nativeBoundingBox": {
            "minx": geoserver_info.nbb_minx,
            "maxx": geoserver_info.nbb_maxx,
            "miny": geoserver_info.nbb_miny,
            "maxy": geoserver_info.nbb_maxy,
            "crs": geoserver_info.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_info.llb_minx,
            "maxx": geoserver_info.llb_maxx,
            "miny": geoserver_info.llb_miny,
            "maxy": geoserver_info.llb_maxy,
            "crs": geoserver_info.llb_crs,
        },
        "enabled": layer_subscription.enabled,
        # "keywords":, #?
    }
    geoserver.upload_layer_wms(workspace=layer_subscription.workspace, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context)

def _publish_postgis(
        publish_entry: "PublishEntry", 
        catalogue_entry: "CatalogueEntry", 
        layer_subscription: "layer_subscriptions.LayerSubscription",
        geoserver:geoserver.GeoServer,
        geoserver_info:GeoServerPublishChannel
    ):
    context = {
      "name": layer_subscription.name,
      "description": layer_subscription.description,
      "enabled": layer_subscription.enabled,
      "capability_url": layer_subscription.url,
      "username": layer_subscription.username,
      "password": layer_subscription.userpassword,
      "database": {
          "host": layer_subscription.host,
          "port": layer_subscription.port,
          "database": layer_subscription.database,
          "schema": layer_subscription.schema,
          "username": layer_subscription.username,
          "password": layer_subscription.userpassword,
          "fetch_size": layer_subscription.fetch_size,
          "connection_timeout": layer_subscription.connection_timeout,
        #   "batch_insert_size": , #?
          "min_connections": layer_subscription.min_connections,
        #   "loose_bbox": _has_override_bbox(publish_entry.geoserver_channel), #?
          "max_connections": layer_subscription.max_connections,
        #   "test_while_idle": , #?
        #   "estimated_extends":, #?
        #   "ssl_mode":, #?
      }
    }
    geoserver.upload_store_postgis(workspace=layer_subscription.workspace, store_name=layer_subscription.name, context=context)
        
    context = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description,
        "title": catalogue_entry.name,
        "abstract": None,
        "native_name": catalogue_entry.mapping_name,
        "crs": geoserver_info.srs,
        "native_crs":geoserver_info.native_crs,
        "override_bbox": geoserver_info.override_bbox,
        "nativeBoundingBox": {
            "minx": geoserver_info.nbb_minx,
            "maxx": geoserver_info.nbb_maxx,
            "miny": geoserver_info.nbb_miny,
            "maxy": geoserver_info.nbb_maxy,
            "crs": geoserver_info.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_info.llb_minx,
            "maxx": geoserver_info.llb_maxx,
            "miny": geoserver_info.llb_miny,
            "maxy": geoserver_info.llb_maxy,
            "crs": geoserver_info.llb_crs,
        },
        "enabled": layer_subscription.enabled,
        # "attributes": catalogue_entry.attributes.all()
        # "description": "TES",
        # "enabled": 'true',
        # "capability_url" :"https://services.slip.wa.gov.au/arcgis/services/DBCA_Restricted_Services/DBCA_Fire_Preview_WFS/MapServer/WFSServer?service=wfs&request=GetCapabilities"
    }
        #     context = {
        #     "name": self.publish_entry.catalogue_entry.metadata.name+"_wfs",
        #     "description": "TES",
        #     "enabled": 'true',
        #     "capability_url" :"https://services.slip.wa.gov.au/arcgis/services/DBCA_Restricted_Services/DBCA_Fire_Preview_WFS/MapServer/WFSServer?service=wfs&request=GetCapabilities"
        # }
    geoserver.upload_layer_wfs(workspace=layer_subscription.workspace, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context)  # We can use ths function for postgis, too.
