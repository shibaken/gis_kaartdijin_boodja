"""Kaartdijin Boodja Publisher Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin

# Local
from govapp.apps.publisher import models


# Register Models
admin.site.register(models.publish_channels.CDDPPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.GeoServerPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_entries.PublishEntry, reversion.admin.VersionAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
