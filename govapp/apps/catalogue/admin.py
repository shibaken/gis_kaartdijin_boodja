"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin

# Local
from govapp.apps.catalogue import models


class CatalogueEntryAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for Catalogue Entries."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    filter_horizontal = ["editors"]


# Register Models
admin.site.register(models.catalogue_entries.CatalogueEntry, CatalogueEntryAdmin)
admin.site.register(models.custodians.Custodian, reversion.admin.VersionAdmin)
admin.site.register(models.layer_attributes.LayerAttribute, reversion.admin.VersionAdmin)
admin.site.register(models.layer_metadata.LayerMetadata, reversion.admin.VersionAdmin)
admin.site.register(models.layer_submissions.LayerSubmission, reversion.admin.VersionAdmin)
admin.site.register(models.layer_subscriptions.LayerSubscription, reversion.admin.VersionAdmin)
admin.site.register(models.layer_symbology.LayerSymbology, reversion.admin.VersionAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
admin.site.register(models.notifications.WebhookNotification, reversion.admin.VersionAdmin)
