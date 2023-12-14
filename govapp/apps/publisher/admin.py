"""Kaartdijin Boodja Publisher Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin

# Local
from govapp.apps.publisher import models


class PublishEntryAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for Publish Entries."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    filter_horizontal = ["editors"]
    list_display = ('id', 'catalogue_entry', 'status', 'published_at')
    ordering = ('-id',)
    
class GeoServerPoolAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for GeoServer Pool."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    list_display = ('id', 'url', 'username', 'enabled', 'created_at')
    ordering = ('id',)
    
class GeoServerQueueAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for GeoServer Queue."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    list_display = ('id', 'publish_entry', 'symbology_only', 'status', 'success', 'submitter','started_at', 'completed_at', 'created_at')
    ordering = ('-id',)
    raw_id_fields = ('submitter',)

class FTPPublishChannelAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for GeoServer Pool."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    list_display = ('id', 'name', 'ftp_server', 'format', 'frequency','published_at','publish_entry','created')
    ordering = ('id',)
    raw_id_fields = ('ftp_server','publish_entry')


# Register Models

admin.site.register(models.publish_channels.FTPServer, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.FTPPublishChannel, FTPPublishChannelAdmin)
admin.site.register(models.publish_channels.CDDPPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.GeoServerPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_entries.PublishEntry, PublishEntryAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
admin.site.register(models.workspaces.Workspace, reversion.admin.VersionAdmin)
admin.site.register(models.geoserver_pools.GeoServerPool, GeoServerPoolAdmin)
admin.site.register(models.geoserver_queues.GeoServerQueue, GeoServerQueueAdmin)
