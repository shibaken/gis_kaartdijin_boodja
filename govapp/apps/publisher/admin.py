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
    ordering = ('id',)
    
class GeoServerPoolAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for GeoServer Pool."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    list_display = ('id', 'url', 'username', 'enabled', 'created_at')
    ordering = ('id',)

# Register Models
admin.site.register(models.publish_channels.CDDPPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.GeoServerPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_entries.PublishEntry, PublishEntryAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
admin.site.register(models.workspaces.Workspace, reversion.admin.VersionAdmin)
admin.site.register(models.geoserver_pool.GeoServerPool, GeoServerPoolAdmin)
