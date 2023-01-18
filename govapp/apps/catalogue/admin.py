"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin

# Local
from . import models


# Register Models
admin.site.register(models.catalogue_entries.CatalogueEntry, reversion.admin.VersionAdmin)
admin.site.register(models.custodians.Custodian, reversion.admin.VersionAdmin)
admin.site.register(models.layer_attributes.LayerAttribute, reversion.admin.VersionAdmin)
admin.site.register(models.layer_metadata.LayerMetadata, reversion.admin.VersionAdmin)
admin.site.register(models.layer_submissions.LayerSubmission, reversion.admin.VersionAdmin)
admin.site.register(models.layer_subscriptions.LayerSubscription, reversion.admin.VersionAdmin)
admin.site.register(models.layer_symbology.LayerSymbology, reversion.admin.VersionAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
admin.site.register(models.notifications.WebhookNotification, reversion.admin.VersionAdmin)
admin.site.register(models.workspaces.Workspace, reversion.admin.VersionAdmin)
