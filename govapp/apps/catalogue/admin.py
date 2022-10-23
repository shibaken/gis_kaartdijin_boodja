"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django.contrib import admin

# Local
from . import models


# Register Models
admin.site.register(models.catalogue_entries.CatalogueEntry)
admin.site.register(models.layer_attributes.LayerAttribute)
admin.site.register(models.layer_metadata.LayerMetadata)
admin.site.register(models.layer_submissions.LayerSubmission)
admin.site.register(models.layer_subscriptions.LayerSubscription)
admin.site.register(models.layer_symbology.LayerSymbology)
admin.site.register(models.notifications.EmailNotification)
admin.site.register(models.notifications.WebhookNotification)
