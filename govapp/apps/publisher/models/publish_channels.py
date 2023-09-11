"""Kaartdijin Boodja Publisher Django Application Publish Channel Models."""


# Standard
import logging
import pathlib
import shutil
import os

# Third-Party
from django import conf
from django.db import models
from django.core import exceptions
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
    GEOJSON = 4

class FTPPublishChannelFormat(models.IntegerChoices):
    """Enumeration for a Publish Channel Format."""
    GEOPACKAGE = 1
    SHAPEFILE = 2
    GEODATABASE = 3
    GEOJSON = 4

@reversion.register()
class CDDPPublishChannel(mixins.RevisionedMixin):
    """Model for a CDDP Publish Channel."""
    
    name = models.TextField(blank=True, null=True, default='')
    #description = models.TextField(blank=True)    
    published_at = models.DateTimeField(blank=True, null=True)
    format = models.IntegerField(choices=CDDPPublishChannelFormat.choices)  # noqa: A003
    mode = models.IntegerField(choices=CDDPPublishChannelMode.choices)
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    path = models.TextField()
    publish_entry = models.ForeignKey(
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

    # @property
    # def name(self) -> str:
    #     """Proxies the Publish Entry's name to this model.

    #     Returns:
    #         str: Name of the Publish Entry.
    #     """
    #     # Retrieve and Return
    #     return self.publish_entry.name

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
        print ('publish_azure')
        print (self.publish_entry.catalogue_entry.active_layer.file)
       
        # Retrieve the Layer File from Storage
        # filepath = sharepoint.sharepoint_input().get_from_url(
        #     url=self.publish_entry.catalogue_entry.active_layer.file,
        # )
        
        filepath = pathlib.Path(self.publish_entry.catalogue_entry.active_layer.file)        

        # Select Conversion Function
        match self.format:
            case CDDPPublishChannelFormat.GEOPACKAGE:
                function = gis.conversions.to_geopackage
            case CDDPPublishChannelFormat.SHAPEFILE:
                function = gis.conversions.to_shapefile
            case CDDPPublishChannelFormat.GEODATABASE:
                function = gis.conversions.to_geodatabase
            case CDDPPublishChannelFormat.GEOJSON:
                function = gis.conversions.to_geojson

        # Convert Layer to Chosen Format
        # converted = function(
        #     filepath=filepath,
        #     layer=self.publish_entry.catalogue_entry.metadata.name,
        # )
        publish_directory = function(
            filepath=filepath,
            layer=self.name,
            catalogue_name=self.publish_entry.catalogue_entry.name,
            export_method='cddp'
        )

        # # Construct Path
        output_path = pathlib.Path(conf.settings.AZURE_OUTPUT_SYNC_DIRECTORY+"/"+self.path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        geodb_dir = ""
        if self.format == 3:
            file_names_geodb = os.listdir(publish_directory['uncompressed_filepath'])
            if len(file_names_geodb) == 1:
                geodb_dir = file_names_geodb[0]

        file_names = os.listdir(pathlib.Path(str(publish_directory['uncompressed_filepath'])+'/'+str(geodb_dir)))
        for file_name in file_names:            
            new_output_path = os.path.join(output_path,file_name)
            if self.format == 3:
                if os.path.isdir(new_output_path): 
                    shutil.rmtree(new_output_path)
            else:
                if os.path.isfile(new_output_path):                    
                        os.remove(new_output_path)   
            shutil.move(os.path.join(pathlib.Path(str(publish_directory['uncompressed_filepath'])+'/'+str(geodb_dir)), file_name), output_path)
            
        # # Push to Azure
        # azure.azure_output().put(
        #     path=publish_path,
        #     contents=converted.read_bytes(),
        # )

        # Delete local temporary copy of file if we can
        # shutil.rmtree(filepath.parent, ignore_errors=True)

    def publish_sharepoint(self) -> None:
        """Publishes the Catalogue Entry to SharePoint if applicable."""
        # Log
        log.info(f"Publishing '{self}' to SharePoint")

        # Retrieve the Layer File from Storage
        # filepath = sharepoint.sharepoint_input().get_from_url(
        #     url=self.publish_entry.catalogue_entry.active_layer.file,
        # )
        filepath = pathlib.Path(self.publish_entry.catalogue_entry.active_layer.file)  

        
        # Select Conversion Function
        match self.format:
            case CDDPPublishChannelFormat.GEOPACKAGE:
                function = gis.conversions.to_geopackage
            case CDDPPublishChannelFormat.SHAPEFILE:
                function = gis.conversions.to_shapefile
            case CDDPPublishChannelFormat.GEODATABASE:
                function = gis.conversions.to_geodatabase
            case CDDPPublishChannelFormat.GEOJSON:
                function = gis.conversions.to_geojson

        # Convert Layer to Chosen Format
        publish_directory = function(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            catalogue_name=self.publish_entry.catalogue_entry.name,
            export_method='cddp'
        )    


        # Construct Path
        #publish_directory = pathlib.Path(conf.settings.SHAREPOINT_OUTPUT_PUBLISH_AREA)
        #publish_path = str(publish_directory / self.path / converted.name)

        geodb_dir = ""
        if self.format == 3:
            file_names_geodb = os.listdir(publish_directory['uncompressed_filepath'])
            if len(file_names_geodb) == 1:
                geodb_dir = file_names_geodb[0]
            

        # Push to Sharepoint
        file_names = os.listdir(os.path.join(publish_directory['uncompressed_filepath'],geodb_dir))        
        for file_name in file_names:            
            new_output_path = os.path.join(conf.settings.SHAREPOINT_OUTPUT_PUBLISH_AREA,self.path,file_name)            
            sharepoint.sharepoint_output().put(
                path=new_output_path,
                contents=pathlib.Path(os.path.join(publish_directory['uncompressed_filepath'],geodb_dir,file_name)).read_bytes(),
            )

            # sharepoint.sharepoint_output().put(
            #     path=os.path.join(conf.settings.SHAREPOINT_OUTPUT_PUBLISH_AREA,filepath),
            #     contents=pathlib.Path(converted['compressed_filepath']).read_bytes(),
            # )

        # Delete local temporary copy of file if we can
        #shutil.rmtree(filepath.parent, ignore_errors=True)


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
    srs = models.CharField(null=True, blank=True, max_length=500)
    override_bbox = models.BooleanField(default=False)
    native_crs = models.CharField(null=True, blank=True, max_length=500)    # will become required, if overried_box is True
    nbb_minx = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    nbb_maxx = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    nbb_miny = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    nbb_maxy = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    nbb_crs = models.CharField(null=True, blank=True, max_length=500)   # will become required, if overried_box is True
    llb_minx = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    llb_maxx = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    llb_miny = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    llb_maxy = models.CharField(null=True, blank=True, max_length=500)  # will become required, if overried_box is True
    llb_crs = models.CharField(null=True, blank=True, max_length=500)   # will become required, if overried_box is True
    active = models.BooleanField(null=True, blank=True,)

    class Meta:
        """GeoServer Publish Channel Model Metadata."""
        verbose_name = "GeoServer Publish Channel"
        verbose_name_plural = "GeoServer Publish Channels"

    def clean(self):
        if not self.override_bbox:
            return
        if self._has_null(self.native_crs, 
                           self.nbb_minx, self.nbb_maxx, self.nbb_miny, self.nbb_maxy, self.nbb_crs,
                           self.llb_minx, self.llb_maxx, self.llb_miny, self.llb_maxy, self.llb_crs):
            raise exceptions.ValidationError("If override_bbox is True, every related fields must be filled.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def _has_null(*args):
        for arg in args:
            if arg is None:
                return True
        return False
        
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

    def publish(self, symbology_only: bool = False, geoserver: gis.geoserver.GeoServer = None) -> None:
        """Publishes the Catalogue Entry to this channel if applicable.

        Args:
            symbology_only (bool): Whether to publish symbology only.
        """
        # Log
        log.info(f"Attempting to publish '{self.publish_entry}' to channel '{self}'")

        # if not geoserver:
        #     geoserver = gis.geoserver.geoserver()

        # Publish Symbology
        self.publish_geoserver_symbology(geoserver=geoserver)

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
                self.publish_geoserver_layer(wms=True, wfs=False, geoserver=geoserver)

            case GeoServerPublishChannelMode.WMS_AND_WFS:
                # Publish to GeoServer (WMS and WFS)
                self.publish_geoserver_layer(wms=True, wfs=True, geoserver=geoserver)

        # Update Published At
        publish_time = timezone.now()
        self.publish_entry.published_at = publish_time
        self.publish_entry.save()
        self.published_at = publish_time
        self.save()

    def publish_geoserver_symbology(self, geoserver: gis.geoserver.GeoServer) -> None:
        """Publishes the Symbology to GeoServer if applicable."""
        # Log
        log.info(f"Publishing '{self}' (Symbology) to GeoServer")

        # Publish Style to GeoServer
        geoserver.upload_style(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            name=self.publish_entry.catalogue_entry.symbology.name,
            sld=self.publish_entry.catalogue_entry.symbology.sld,
        )

    def publish_geoserver_layer(self, wms: bool, wfs: bool, geoserver: gis.geoserver.GeoServer) -> None:
        """Publishes the Catalogue Entry to GeoServer if applicable.

        Args:
            wms (bool): Whether to enable WMS capabilities.
            wfs (bool): Whether to enable WFS capabilities.
        """
        # Log
        log.info(f"Publishing '{self}' (Layer) to GeoServer")

        # Retrieve the Layer File from Storage
        # filepath = sharepoint.sharepoint_input().get_from_url(
        #     url=self.publish_entry.catalogue_entry.active_layer.file,
        # )
        filepath = pathlib.Path(self.publish_entry.catalogue_entry.active_layer.file) 
 
        # Convert Layer to GeoPackage
        geopackage = gis.conversions.to_geopackage(
            filepath=filepath,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            catalogue_name=self.publish_entry.catalogue_entry.name,
            export_method='geoserver'
        )
            
        # Push Layer to GeoServer
        geoserver.upload_geopackage(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            filepath=geopackage['full_filepath'],
        )

        # Set Default Style
        geoserver.set_default_style(
            workspace=self.workspace.name,
            layer=self.publish_entry.catalogue_entry.metadata.name,
            name=self.publish_entry.catalogue_entry.symbology.name,
        )

        ## HERE 
        
        # Delete local temporary copy of file if we can
        #shutil.rmtree(filepath.parent, ignore_errors=True)


@reversion.register()
class FTPServer(mixins.RevisionedMixin):
    """Model for a GeoServer Publish Channel."""
    name = models.CharField(null=True, blank=True, max_length=1024)
    host = models.CharField(null=True, blank=True, max_length=1024)
    username = models.CharField(null=True, blank=True, max_length=500)
    password = models.CharField(null=True, blank=True, max_length=500)
    enabled = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


@reversion.register()
class FTPPublishChannel(mixins.RevisionedMixin):
    """Model for a GeoServer Publish Channel."""
    name = models.CharField(null=True, blank=True, max_length=1024)
    ftp_server = models.ForeignKey(
        FTPServer,
        related_name="publish_channels_ftp_server",
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
    )  
    publish_entry = models.ForeignKey(
        publish_entries.PublishEntry,
        related_name="ftp_channel",
        on_delete=models.CASCADE,
        null=True, 
        blank=True,        
    )
    format = models.IntegerField(choices=FTPPublishChannelFormat.choices) 
    frequency = models.IntegerField(choices=PublishChannelFrequency.choices)
    path = models.CharField(null=True, blank=True, max_length=2048)
    published_at = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name