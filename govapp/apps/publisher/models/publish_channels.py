"""Kaartdijin Boodja Publisher Django Application Publish Channel Models."""


# Standard
import logging
import pathlib
import shutil

# Third-Party
from django import conf
from django.db import models
from django.utils import timezone
import reversion

# Local
from govapp import gis
from govapp.common import azure
from govapp.common import mixins
from govapp.common import sharepoint
from govapp.apps.publisher.models import publish_entries
from govapp.apps.publisher.models import workspaces


# Logging
log = logging.getLogger(__name__)


class PublishChannelFrequency(models.IntegerChoices):
    """Enumeration for a Publish Channel Frequency."""
    ON_CHANGE = 1


class CDDPPublishChannelMode(models.IntegerChoices):
    """Enumeration for a CDDP Publish Channel Mode."""
    AZURE = 1
    AZURE_AND_SHAREPOINT = 2


class CDDPPublishChannelFormat(models.IntegerChoices):
    """Enumeration for a Publish Channel Format."""
    GEOPACKAGE = 1
    SHAPEFILE = 2
    GEODATABASE = 3


@reversion.register()
class CDDPPublishChannel(mixins.RevisionedMixin):
    """Model for a CDDP Publish Channel."""
    #name = models.TextField()
    #description = models.TextField(blank=True)
    published_at = models.DateTimeField(blank=True, null=True)
    format = models.IntegerField(choices=CDDPPublishChannelFormat.choices)  # noqa: A003
    mode = models.IntegerField(choices=CDDPPublishChannelMode.choices)
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    path = models.TextField()
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
        return f"{self.publish_entry.name}"

    @property
    def name(self) -> str:
        """Proxies the Publish Entry's name to this model.

        Returns:
            str: Name of the Publish Entry.
        """
        # Retrieve and Return
        return self.publish_entry.name

    def publish(self, symbology_only: bool = False) -> None:
        """Publishes the Catalogue Entry to this channel if applicable.

        Args:
            symbology_only (bool): Whether to publish symbology only.
        """
        # Log
        log.info(f"Attempting to publish '{self.publish_entry}' to channel '{self}'")

        # Check Symbology Only Flag
        if symbology_only:
            # Log
            log.info(f"Skipping due to {symbology_only=}")

            # Exit Early
            return

        # Check Mode
        match self.mode:
            case CDDPPublishChannelMode.AZURE:
                # Publish only to Azure
                self.publish_azure()

            case CDDPPublishChannelMode.AZURE_AND_SHAREPOINT:
                # Publish to Azure and Sharepoint
                self.publish_azure()
                self.publish_sharepoint()

        # Update Published At
        publish_time = timezone.now()
        self.publish_entry.published_at = publish_time
        self.publish_entry.save()
        self.published_at = publish_time
        self.save()

    def publish_azure(self) -> None:
        """Publishes the Catalogue Entry to Azure if applicable."""
        # Log
        log.info(f"Publishing '{self}' to Azure")

        # Retrieve the Layer File from Storage
        filepath = sharepoint.sharepoint_input().get_from_url(
            url=self.publish_entry.catalogue_entry.active_layer.file,
        )

        # Select Conversion Function
        match self.format:
            case CDDPPublishChannelFormat.GEOPACKAGE:
                function = gis.conversions.to_geopackage
            case CDDPPublishChannelFormat.SHAPEFILE:
                function = gis.conversions.to_shapefile
            case CDDPPublishChannelFormat.GEODATABASE:
                function = gis.conversions.to_geodatabase

        # Convert Layer to Chosen Format
        converted = function(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
        )

        # Construct Path
        publish_directory = pathlib.Path(self.path)
        publish_path = str(publish_directory / converted.name)

        # Push to Azure
        azure.azure_output().put(
            path=publish_path,
            contents=converted.read_bytes(),
        )

        # Delete local temporary copy of file if we can
        shutil.rmtree(filepath.parent, ignore_errors=True)

    def publish_sharepoint(self) -> None:
        """Publishes the Catalogue Entry to SharePoint if applicable."""
        # Log
        log.info(f"Publishing '{self}' to SharePoint")

        # Retrieve the Layer File from Storage
        filepath = sharepoint.sharepoint_input().get_from_url(
            url=self.publish_entry.catalogue_entry.active_layer.file,
        )

        # Select Conversion Function
        match self.format:
            case CDDPPublishChannelFormat.GEOPACKAGE:
                function = gis.conversions.to_geopackage
            case CDDPPublishChannelFormat.SHAPEFILE:
                function = gis.conversions.to_shapefile
            case CDDPPublishChannelFormat.GEODATABASE:
                function = gis.conversions.to_geodatabase

        # Convert Layer to Chosen Format
        converted = function(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
        )

        # Construct Path
        publish_directory = pathlib.Path(conf.settings.SHAREPOINT_OUTPUT_PUBLISH_AREA)
        publish_path = str(publish_directory / self.path / converted.name)

        # Push to Sharepoint
        sharepoint.sharepoint_output().put(
            path=publish_path,
            contents=converted.read_bytes(),
        )

        # Delete local temporary copy of file if we can
        shutil.rmtree(filepath.parent, ignore_errors=True)


class GeoServerPublishChannelMode(models.IntegerChoices):
    """Enumeration for a GeoServer Publish Channel Mode."""
    WMS = 1
    WMS_AND_WFS = 2


@reversion.register()
class GeoServerPublishChannel(mixins.RevisionedMixin):
    """Model for a GeoServer Publish Channel."""
    #name = models.TextField()
    #description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(blank=True, null=True)
    mode = models.IntegerField(choices=GeoServerPublishChannelMode.choices)
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    workspace = models.ForeignKey(
        workspaces.Workspace,
        related_name="publish_channels",
        on_delete=models.PROTECT,
    )
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
        return f"{self.publish_entry.catalogue_entry.name}"

    @property
    def name(self) -> str:
        """Proxies the Publish Entry's name to this model.

        Returns:
            str: Name of the Publish Entry.
        """
        # Retrieve and Return
        return self.publish_entry.name

    def publish(self, symbology_only: bool = False) -> None:
        """Publishes the Catalogue Entry to this channel if applicable.

        Args:
            symbology_only (bool): Whether to publish symbology only.
        """
        # Log
        log.info(f"Attempting to publish '{self.publish_entry}' to channel '{self}'")

        # Publish Symbology
        self.publish_geoserver_symbology()

        # Check Symbology Only Flag
        if symbology_only:
            # Log
            log.info(f"Skipping due to {symbology_only=}")

            # Exit Early
            return

        # Check Mode
        match self.mode:
            case GeoServerPublishChannelMode.WMS:
                # Publish to GeoServer (WMS Only)
                self.publish_geoserver_layer(wms=True, wfs=False)

            case GeoServerPublishChannelMode.WMS_AND_WFS:
                # Publish to GeoServer (WMS and WFS)
                self.publish_geoserver_layer(wms=True, wfs=True)

        # Update Published At
        publish_time = timezone.now()
        self.publish_entry.published_at = publish_time
        self.publish_entry.save()
        self.published_at = publish_time
        self.save()

    def publish_geoserver_symbology(self) -> None:
        """Publishes the Symbology to GeoServer if applicable."""
        # Log
        log.info(f"Publishing '{self}' (Symbology) to GeoServer")

        # Publish Style to GeoServer
        gis.geoserver.geoserver().upload_style(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            name=self.publish_entry.catalogue_entry.symbology.name,
            sld=self.publish_entry.catalogue_entry.symbology.sld,
        )

    def publish_geoserver_layer(self, wms: bool, wfs: bool) -> None:
        """Publishes the Catalogue Entry to GeoServer if applicable.

        Args:
            wms (bool): Whether to enable WMS capabilities.
            wfs (bool): Whether to enable WFS capabilities.
        """
        # Log
        log.info(f"Publishing '{self}' (Layer) to GeoServer")

        # Retrieve the Layer File from Storage
        filepath = sharepoint.sharepoint_input().get_from_url(
            url=self.publish_entry.catalogue_entry.active_layer.file,
        )

        # Convert Layer to GeoPackage
        geopackage = gis.conversions.to_geopackage(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
        )

        # Push Layer to GeoServer
        gis.geoserver.geoserver().upload_geopackage(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            filepath=geopackage,
        )

        # Set Default Style
        gis.geoserver.geoserver().set_default_style(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            name=self.publish_entry.catalogue_entry.symbology.name,
        )

        # Delete local temporary copy of file if we can
        shutil.rmtree(filepath.parent, ignore_errors=True)
