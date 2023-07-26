"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin
from django.contrib import auth

# Local
from govapp.apps.catalogue import models

# class CatalogueModelAdmin(reversion.admin.VersionAdmin):
#     ordering = ('id', 'name')
    
    
class CatalogueEntryPermissionInline(admin.TabularInline):
    model = models.permission.CatalogueEntryPermission

class CatalogueEntryAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for Catalogue Entries."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    # filter_horizontal = ["editors"]
    list_display = ('id', 'name', 'status', 'created_at', 'updated_at')
    ordering = ('id',)
    inlines = [CatalogueEntryPermissionInline]
    

class CustodianAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','contact_name','contact_email','contact_phone')
    list_display = ('id', 'name', 'contact_name', 'contact_email', 'contact_phone')
    ordering = ('id',)

class LayerAttributeAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'type', 'order', 'catalogue_entry')
    ordering = ('id',)

class LayerAttributeTypeAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'key', 'name', 'created_at')
    ordering = ('id',)
    
class LayerMetadataAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'created_at', 'catalogue_entry')
    ordering = ('id',)
    
class LayerSubmissionAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'status', 'is_active', 'catalogue_entry', 'created_at')
    ordering = ('id',)

class LayerSubscriptionAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'catalogue_entry', 'name', 'enabled', 'username', 'url', 'host', 'updated_at', 'created_at')
    ordering = ('id',)
    
class LayerSymbologyAdmin(reversion.admin.VersionAdmin):
    search_fields = ('catalogue_entry__id','sld')
    list_display = ('id', 'catalogue_entry', 'sld')
    ordering = ('id',)
    
class EmailNotificationAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','email')
    list_display = ('id', 'name', 'type', 'email', 'active', 'catalogue_entry')
    raw_id_fields = ('catalogue_entry',)
    ordering = ('id',)
    
class WebhookNotificationAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','type', 'url')
    list_display = ('id', 'name', 'type', 'url', 'catalogue_entry')
    ordering = ('id',)

class LayerSubmission(reversion.admin.VersionAdmin):
    search_fields = ('id','catalogue_entry__name','description')
    
    
class CatalogueEntryPermissionAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'user', 'catalogue_entry')
    # inlines = [CatalogueEntryInline]
    

# Register Models
admin.site.register(models.catalogue_entries.CatalogueEntry, CatalogueEntryAdmin)
admin.site.register(models.custodians.Custodian, CustodianAdmin)
admin.site.register(models.layer_attributes.LayerAttribute, LayerAttributeAdmin)
admin.site.register(models.layer_attribute_types.LayerAttributeType, LayerAttributeTypeAdmin)
admin.site.register(models.layer_metadata.LayerMetadata, LayerMetadataAdmin)
admin.site.register(models.layer_submissions.LayerSubmission, LayerSubmissionAdmin)
admin.site.register(models.layer_subscriptions.LayerSubscription, LayerSubscriptionAdmin)
admin.site.register(models.layer_symbology.LayerSymbology, LayerSymbologyAdmin)
admin.site.register(models.notifications.EmailNotification, EmailNotificationAdmin)
admin.site.register(models.notifications.WebhookNotification, WebhookNotificationAdmin)
admin.site.register(models.permission.CatalogueEntryPermission, CatalogueEntryPermissionAdmin)
