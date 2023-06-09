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
    search_fields = ('id','name',)

class CustodianAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','contact_name','contact_email','contact_phone')

class EmailNotificationAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','email')

class LayerSymbologyAdmin(reversion.admin.VersionAdmin):
    search_fields = ('catalogue_entry__id','sld')

class LayerSubmission(reversion.admin.VersionAdmin):
    search_fields = ('id','catalogue_entry__name','description')

# Register Models
admin.site.register(models.catalogue_entries.CatalogueEntry, CatalogueEntryAdmin)
admin.site.register(models.custodians.Custodian, CustodianAdmin)
admin.site.register(models.layer_attributes.LayerAttribute, reversion.admin.VersionAdmin)
admin.site.register(models.layer_metadata.LayerMetadata, reversion.admin.VersionAdmin)
admin.site.register(models.layer_submissions.LayerSubmission, LayerSubmission)
admin.site.register(models.layer_subscriptions.LayerSubscription, reversion.admin.VersionAdmin)
admin.site.register(models.layer_symbology.LayerSymbology, LayerSymbologyAdmin)
admin.site.register(models.notifications.EmailNotification, EmailNotificationAdmin)
admin.site.register(models.notifications.WebhookNotification, reversion.admin.VersionAdmin)
