"""Kaartdijin Boodja Publisher GeoServer Queue Excutor."""

# Standard
import logging

# Third-Party

# Local
from govapp.apps.publisher import notifications as notifications_utils
from govapp.gis import geoserver

# Typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from govapp.apps.publisher.models.publish_entries import PublishEntry

# Logging
log = logging.getLogger(__name__)

"""Publish to GeoServers."""
def publish(publish_entry: "PublishEntry", geoserver:geoserver.GeoServer, symbology_only: bool = False) -> (bool, Exception):
    # def publish_geoserver(self, symbology_only: bool = False) -> None:
    """Publishes to GeoServer channel if applicable.

    Args:
        symbology_only (bool): Flag to only publish symbology.
    """
    # Check for Publish Channel
    if not hasattr(publish_entry, "geoserver_channel"):
        # Log
        log.info(f"'{publish_entry}' has no GeoServer Publish Channel")

        # Exit Early
        return

    # Log
    log.info(f"Publishing '{publish_entry.catalogue_entry}' - '{publish_entry.geoserver_channel}' ({symbology_only=})")

    # Handle Errors
    try:
        # Publish!
        publish_entry.geoserver_channel.publish(symbology_only, geoserver)  # type: ignore[union-attr]

    except Exception as exc:
        # Log
        log.error(f"Unable to publish to GeoServer Publish Channel: {exc}")

        # Send Failure Emails
        notifications_utils.publish_entry_publish_failure(publish_entry)
        
        return False, exc

    else:
        # Send Success Emails
        notifications_utils.publish_entry_publish_success(publish_entry)
        
    return True