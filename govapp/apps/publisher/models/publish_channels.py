"""Kaartdijin Boodja Publisher Django Application Publish Channel Models."""


# Standard
import logging
import shutil

# Third-Party
from django.db import models
import reversion

# Local
from govapp import gis
from govapp.common import mixins
from govapp.common import sharepoint
from govapp.apps.publisher.models import publish_entries


# Logging
log = logging.getLogger(__name__)


class PublishChannelFrequency(models.IntegerChoices):
    """Enumeration for a Publish Channel Frequency."""
    ON_CHANGE = 1
    DAILY = 3
    WEEKLY = 4
    MONTHLY = 5
    QUARTERLY = 6
    YEARLY = 7


@reversion.register()
class CDDPPublishChannel(mixins.RevisionedMixin):
    """Model for a CDDP Publish Channel."""
    name = models.TextField()
    description = models.TextField()
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    publish_entry = models.OneToOneField(
        publish_entries.PublishEntry,
        related_name="cddp_channel",
        on_delete=models.CASCADE,
    )

    class Meta:
        """CDDP Publish Channel Model Metadata."""
        verbose_name = "CDDP Publish Channel"
        verbose_name_plural = "CDDP Publish Channels"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    def publish(self, force: bool = False) -> None:
        """Publishes the Catalogue Entry to this channel if applicable.

        Args:
            force (bool): Force publish, regardless of frequency.
        """
        # Log
        log.info(f"Attempting to publish '{self.publish_entry}' to channel '{self}' ({force=})")

        # Check Frequency
        if self.frequency != PublishChannelFrequency.ON_CHANGE and not force:
            # Do not publish
            log.info(f"Frequency is '{self.frequency}', skipping...")

            # Exit early
            return

        # Publish!
        self.publish_azure()
        self.publish_sharepoint()

    def publish_sharepoint(self) -> None:
        """Publishes the Catalogue Entry to SharePoint if applicable."""
        # Log
        log.info(f"Publishing '{self}' to SharePoint")

        # TODO
        ...

    def publish_azure(self) -> None:
        """Publishes the Catalogue Entry to Azure if applicable."""
        # Log
        log.info(f"Publishing '{self}' to Azure")

        # TODO
        ...


@reversion.register()
class GeoServerPublishChannel(mixins.RevisionedMixin):
    """Model for a GeoServer Publish Channel."""
    name = models.TextField()
    description = models.TextField()
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    publish_entry = models.OneToOneField(
        publish_entries.PublishEntry,
        related_name="geoserver_channel",
        on_delete=models.CASCADE,
    )

    class Meta:
        """GeoServer Publish Channel Model Metadata."""
        verbose_name = "GeoServer Publish Channel"
        verbose_name_plural = "GeoServer Publish Channels"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    def publish(self, force: bool = False) -> None:
        """Publishes the Catalogue Entry to this channel if applicable.

        Args:
            force (bool): Force publish, regardless of frequency.
        """
        # Log
        log.info(f"Attempting to publish '{self.publish_entry}' to channel '{self}' ({force=})")

        # Check Frequency
        if self.frequency != PublishChannelFrequency.ON_CHANGE and not force:
            # Do not publish
            log.info(f"Frequency is '{self.frequency}', skipping...")

            # Exit early
            return

        # Publish!
        self.publish_geoserver()

    def publish_geoserver(self) -> None:
        """Publishes the Catalogue Entry to GeoServer if applicable."""
        # Log
        log.info(f"Publishing '{self}' to GeoServer")

        # Publish Style to GeoServer
        gis.geoserver.GeoServer().upload_style(
            workspace=self.publish_entry.catalogue_entry.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            name=self.publish_entry.catalogue_entry.symbology.name,
            sld=self.publish_entry.catalogue_entry.symbology.sld,
        )

        # Retrieve the Layer File from Storage
        filepath = sharepoint.SharepointStorage().get_from_url(
            url=self.publish_entry.catalogue_entry.active_layer.file,
        )

        # Convert Layer to GeoPackage
        geopackage = gis.conversions.to_geopackage(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
        )

        # Push Layer to GeoServer
        gis.geoserver.GeoServer().upload_geopackage(
            workspace=self.publish_entry.catalogue_entry.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            filepath=geopackage,
        )

        # Delete local temporary copy of file if we can
        shutil.rmtree(filepath.parent, ignore_errors=True)
