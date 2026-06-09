"""Kaartdijin Boodja Publisher GeoServer Queue Excutor."""

# Standard
import logging

import httpx

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
def publish(geoserver_publish_channel: GeoServerPublishChannel , symbology_only: bool = False) -> (bool, Exception):
    """Publishes to GeoServer channel if applicable.

    Args:
        symbology_only (bool): Flag to only publish symbology.
    """
    # Log
    log.info(f"Publishing '{geoserver_publish_channel.publish_entry.catalogue_entry}' - '{geoserver_publish_channel.publish_entry.geoserver_channels}' ({symbology_only=})")

    # Handle Errors
    try:
        ### Publish! ###
        if geoserver_publish_channel.active:
            if geoserver_publish_channel.publish_entry.catalogue_entry.type in [CatalogueEntryType.SPATIAL_FILE, CatalogueEntryType.SUBSCRIPTION_QUERY]:  # In the case of SUBSCRIPTION_QUERY, system generates spatial_file, which 
                # for spatial file
                geoserver_publish_channel.publish(symbology_only)
            else:
                # for layer subscription (SUBSCRIPTION_WFS, SUBSCRIPTION_WMS, SUBSCRIPTION_POSTGIS)
                _publish(geoserver_publish_channel)

            # Handle cached layer
            geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_publish_channel.geoserver_pool.url, geoserver_publish_channel.geoserver_pool.username, geoserver_publish_channel.geoserver_pool.password)
            # if geoserver_publish_channel.create_cached_layer:
            #     ret = geoserver_obj.create_or_update_cached_layer(
            #         geoserver_publish_channel.layer_name_with_workspace,
            #         geoserver_publish_channel.publish_entry.catalogue_entry.type,
            #         geoserver_publish_channel.create_cached_layer,
            #         geoserver_publish_channel.expire_server_cache_after_n_seconds,
            #         geoserver_publish_channel.expire_client_cache_after_n_seconds
            #     )
            # else:
            #     ret = geoserver_obj.delete_cached_layer(geoserver_publish_channel.layer_name_with_workspace)
            ret = geoserver_obj.create_or_update_cached_layer(
                geoserver_publish_channel.layer_name_with_workspace,
                geoserver_publish_channel.publish_entry.catalogue_entry.type,
                geoserver_publish_channel.create_cached_layer,
                geoserver_publish_channel.expire_server_cache_after_n_seconds,
                geoserver_publish_channel.expire_client_cache_after_n_seconds
            )

        else:
            geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_publish_channel.geoserver_pool.url, geoserver_publish_channel.geoserver_pool.username, geoserver_publish_channel.geoserver_pool.password)

            # Check if the layer to be deleted exists in the geoserver
            layers = geoserver_obj.get_layers()
            layer_names = [layer['name'].split(':')[1] for layer in layers]
            if geoserver_publish_channel.publish_entry.catalogue_entry.name in layer_names:
                # Layer exists --> Delete the layer from the geoserver
                geoserver_obj.delete_layer(geoserver_publish_channel.publish_entry.catalogue_entry.name)


    except Exception as exc:
        # Log
        log.error(f"Unable to publish to GeoServer Publish Channel: {exc}")

        # Send Failure Emails
        notifications_utils.publish_entry_publish_failure(geoserver_publish_channel.publish_entry)
        
        return False, exc

    else:
        # Send Success Emails
        notifications_utils.publish_entry_publish_success(geoserver_publish_channel.publish_entry)
        
    return True, None

def _publish(geoserver_publish_channel:GeoServerPublishChannel):
    layer_subscription = geoserver_publish_channel.publish_entry.catalogue_entry.layer_subscription
    
    if layer_subscription.type == layer_subscriptions.LayerSubscriptionType.WFS:
        _publish_wfs(geoserver_publish_channel)
    elif layer_subscription.type == layer_subscriptions.LayerSubscriptionType.WMS:
        _publish_wms(geoserver_publish_channel)
    elif layer_subscription.type == layer_subscriptions.LayerSubscriptionType.POST_GIS:
        _publish_postgis(geoserver_publish_channel)


def _publish_wfs(
        geoserver_publish_channel:GeoServerPublishChannel
    ):
    catalogue_entry = geoserver_publish_channel.publish_entry.catalogue_entry
    layer_subscription = catalogue_entry.layer_subscription
    geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_publish_channel.geoserver_pool.url, geoserver_publish_channel.geoserver_pool.username, geoserver_publish_channel.geoserver_pool.password)

    context = {
      "name": layer_subscription.name,
      "description": layer_subscription.description,
      "enabled": layer_subscription.enabled,
      "capability_url": layer_subscription.url,
      "username": layer_subscription.username,
      "password": layer_subscription.userpassword,
    }
    geoserver_obj.upload_store_wfs(workspace=layer_subscription.workspace, store_name=layer_subscription.name, context=context)

    context = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description,
        "native_name":catalogue_entry.mapping_name,
        "title":catalogue_entry.name,
        "abstract": None,
        "override_bbox": geoserver_publish_channel.override_bbox,
        "native_crs":geoserver_publish_channel.native_crs,
        "crs": geoserver_publish_channel.srs,
        "nativeBoundingBox": {
            "minx": geoserver_publish_channel.nbb_minx,
            "maxx": geoserver_publish_channel.nbb_maxx,
            "miny": geoserver_publish_channel.nbb_miny,
            "maxy": geoserver_publish_channel.nbb_maxy,
            "crs": geoserver_publish_channel.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_publish_channel.llb_minx,
            "maxx": geoserver_publish_channel.llb_maxx,
            "miny": geoserver_publish_channel.llb_miny,
            "maxy": geoserver_publish_channel.llb_maxy,
            "crs": geoserver_publish_channel.llb_crs,
        },
        "enabled": "true",
        # "keywords":, #?
    }
    geoserver_obj.upload_layer_wfs(workspace=layer_subscription.workspace.name, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context)


def _publish_wms(geoserver_publish_channel: "GeoServerPublishChannel"):
    """Publishes a WMS layer. Works generically for any WMS provider."""
    catalogue_entry = geoserver_publish_channel.publish_entry.catalogue_entry
    layer_subscription = catalogue_entry.layer_subscription
    workspace_name = layer_subscription.workspace.name
    safe_store_name = layer_subscription.name.replace(" ", "_")
    
    # 1. Instantiate GeoServer with all 3 required arguments
    pool = geoserver_publish_channel.geoserver_pool
    geoserver_obj = geoserver.geoserverWithCustomCreds(pool.url, pool.username, pool.password)

    # log.info(f"Force deleting old store [{safe_store_name}] to clear bad metadata...")
    # try:
    #     delete_url = f"{geoserver_obj.service_url}/rest/workspaces/{workspace_name}/wmsstores/{safe_store_name}?recurse=true"
    #     with httpx.Client(auth=geoserver_obj.auth) as client:
    #         client.delete(delete_url, timeout=30.0)
    # except Exception as e:
    #     log.debug(f"Delete failed (probably not exists), safe to ignore: {e}")
    from urllib.parse import quote
    for name_to_del in [layer_subscription.name, safe_store_name]:
        try:
            enc_name = quote(name_to_del)
            del_url = f"{geoserver_obj.service_url}/rest/workspaces/{workspace_name}/wmsstores/{enc_name}?recurse=true"
            with httpx.Client(auth=geoserver_obj.auth) as client:
                client.delete(del_url, timeout=30.0)
        except Exception:
            pass
    
    # 2. Universal URL Normalization
    # Clean the URL by removing existing query parameters
    url = layer_subscription.url.split('?')[0].rstrip('/')
    
    # Fix endpoints for specific known strict servers (like DEA)
    if "ows.dea.ga.gov.au" in url.lower() and not url.lower().endswith("/wms"):
        url = f"{url}/wms"
    
    # Standard OGC parameters: works for both old and new servers.
    # We use WMS 1.1.1 as the most widely compatible baseline.
    # url = f"{url}?SERVICE=WMS&VERSION=1.1.1"
    # url = f"{url}?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities"


    context_store = {
        "name": safe_store_name, # Use safe store name with underscores to avoid GeoServer issues
        "capability_url": url,
        "workspace": workspace_name,
        "enabled": layer_subscription.enabled,
        "username": layer_subscription.username,
        "password": layer_subscription.userpassword,
        "geoserver_setting": {
            "max_connections": layer_subscription.max_connections,
            "read_timeout": layer_subscription.read_timeout,
            "connect_timeout": layer_subscription.connection_timeout,
        }
    }
    # Create or Update Store
    geoserver_obj.upload_store_wms(workspace=workspace_name, store_name=layer_subscription.name, context=context_store)

    # Allow GeoServer catalog to sync
    import time
    time.sleep(1)
    # geoserver_obj.reload_store(workspace=workspace_name, store_name=safe_store_name) 
    geoserver_obj.reload_catalog()
    time.sleep(2)

    # 3. Layer Context: Use mapping_name as the safe ID (slug) for ALL systems
    context_layer = {
        "name": catalogue_entry.mapping_name, # Slug (e.g. 'ga_s2m_fmc_mosaic')
        "title": catalogue_entry.name,        # Human readable (e.g. 'Fuel Moisture...')
        "native_name": catalogue_entry.mapping_name,
        "crs": geoserver_publish_channel.srs,
        "native_crs": geoserver_publish_channel.native_crs,
        "override_bbox": True,
        "nativeBoundingBox": {
            "minx": geoserver_publish_channel.nbb_minx,
            "maxx": geoserver_publish_channel.nbb_maxx,
            "miny": geoserver_publish_channel.nbb_miny,
            "maxy": geoserver_publish_channel.nbb_maxy,
            "crs": geoserver_publish_channel.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_publish_channel.llb_minx,
            "maxx": geoserver_publish_channel.llb_maxx,
            "miny": geoserver_publish_channel.llb_miny,
            "maxy": geoserver_publish_channel.llb_maxy,
            "crs": geoserver_publish_channel.llb_crs,
        },
        "enabled": layer_subscription.enabled,
    }
    
    # Use mapping_name (identifier) for the GeoServer resource name
    geoserver_obj.upload_layer_wms(
        workspace=workspace_name,
        store_name=safe_store_name,
        layer_name=catalogue_entry.mapping_name,
        context=context_layer
    )


def _publish_wms_old(
        geoserver_publish_channel:GeoServerPublishChannel
    ):
    catalogue_entry = geoserver_publish_channel.publish_entry.catalogue_entry
    layer_subscription = catalogue_entry.layer_subscription
    
    # 1. Universal URL and Version Handling
    original_url = layer_subscription.url
    # Extract version from URL if present (e.g., VERSION=1.3.0)
    import re
    version_match = re.search(r'VERSION=([\d\.]+)', original_url, re.IGNORECASE)
    wms_version = version_match.group(1) if version_match else "1.1.1" # Default to 1.1.1 (widely compatible)

    # Base URL: Strip query parameters to let GeoServer manage them
    base_url = original_url.split('?')[0].rstrip('/')
    
    # Domain-specific adjustment (DEA specific fix but safe for others)
    if "ows.dea.ga.gov.au" in base_url.lower() and not base_url.lower().endswith("/wms"):
        base_url = f"{base_url}/wms"

    context_store = {
        "name": layer_subscription.name,
        "description": layer_subscription.description,
        "enabled": layer_subscription.enabled,
        "capability_url": base_url,
        "wms_version": wms_version, # Pass detected or default version
        "username": layer_subscription.username,
        "password": layer_subscription.userpassword,
        "workspace": layer_subscription.workspace.name,
        "geoserver_setting": {
            "max_connections": layer_subscription.max_connections,
            "read_timeout": layer_subscription.read_timeout,
            "connect_timeout": layer_subscription.connection_timeout,
        }
    }
    geoserver_obj = geoserver.geoserverWithCustomCreds(...)
    geoserver_obj.upload_store_wms(workspace=layer_subscription.workspace.name, store_name=layer_subscription.name, context=context_store)

    # 2. Layer metadata passing
    context_layer = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description or "",
        "native_name": catalogue_entry.mapping_name,
        "title": catalogue_entry.name,
        "abstract": "",
        "override_bbox": True, # Always provide BBOX to avoid GeoServer probing
        "native_crs": geoserver_publish_channel.native_crs,
        "crs": geoserver_publish_channel.srs,
        "nativeBoundingBox": {
            "minx": geoserver_publish_channel.nbb_minx,
            "maxx": geoserver_publish_channel.nbb_maxx,
            "miny": geoserver_publish_channel.nbb_miny,
            "maxy": geoserver_publish_channel.nbb_maxy,
            "crs": geoserver_publish_channel.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_publish_channel.llb_minx,
            "maxx": geoserver_publish_channel.llb_maxx,
            "miny": geoserver_publish_channel.llb_miny,
            "maxy": geoserver_publish_channel.llb_maxy,
            "crs": geoserver_publish_channel.llb_crs,
        },
        "enabled": layer_subscription.enabled,
    }
    geoserver_obj.upload_layer_wms(workspace=layer_subscription.workspace, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context_layer)


def _publish_postgis(
        geoserver_publish_channel:GeoServerPublishChannel
    ):
    catalogue_entry = geoserver_publish_channel.publish_entry.catalogue_entry
    layer_subscription = catalogue_entry.layer_subscription
    geoserver_obj = geoserver.geoserverWithCustomCreds(geoserver_publish_channel.geoserver_pool.url, geoserver_publish_channel.geoserver_pool.username, geoserver_publish_channel.geoserver_pool.password)

    # Publish Symbology
    geoserver_publish_channel.publish_geoserver_symbology(geoserver=geoserver_obj)

    context = {
      "name": layer_subscription.name,
      "namespace": f'http://{layer_subscription.workspace.name}',
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
          "min_connections": layer_subscription.min_connections,
          "max_connections": layer_subscription.max_connections,
          "ssl_mode": layer_subscription.get_ssl_mode_display(),
      }
    }
    geoserver_obj.upload_store_postgis(workspace=layer_subscription.workspace, store_name=layer_subscription.name, context=context)
        
    context = {
        "name": catalogue_entry.name,
        "description": catalogue_entry.description,
        "title": catalogue_entry.name,
        "abstract": None,
        "native_name": catalogue_entry.mapping_name,
        "crs": geoserver_publish_channel.srs,
        "native_crs":geoserver_publish_channel.native_crs,
        "override_bbox": geoserver_publish_channel.override_bbox,
        "nativeBoundingBox": {
            "minx": geoserver_publish_channel.nbb_minx,
            "maxx": geoserver_publish_channel.nbb_maxx,
            "miny": geoserver_publish_channel.nbb_miny,
            "maxy": geoserver_publish_channel.nbb_maxy,
            "crs": geoserver_publish_channel.nbb_crs,
        },
        "latLonBoundingBox": {
            "minx": geoserver_publish_channel.llb_minx,
            "maxx": geoserver_publish_channel.llb_maxx,
            "miny": geoserver_publish_channel.llb_miny,
            "maxy": geoserver_publish_channel.llb_maxy,
            "crs": geoserver_publish_channel.llb_crs,
        },
        "enabled": layer_subscription.enabled,
    }
    geoserver_obj.upload_layer_wfs(workspace=layer_subscription.workspace, store_name=layer_subscription.name, layer_name=catalogue_entry.name, context=context)  # We can use ths function for postgis, too.

    style_name = catalogue_entry.symbology.name if hasattr(catalogue_entry, 'symbology') and catalogue_entry.symbology.name and catalogue_entry.symbology.sld else 'generic'
    geoserver_obj.set_default_style_to_layer(
        style_name=style_name,
        workspace_name=layer_subscription.workspace,
        layer_name=catalogue_entry.name,
    )