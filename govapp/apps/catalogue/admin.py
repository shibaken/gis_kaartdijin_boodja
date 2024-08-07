"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin
from django.contrib import auth
from django.utils.html import format_html

# Local
from govapp.apps.catalogue import models
from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntryStatus
from govapp.apps.catalogue.models.layer_submissions import LayerSubmissionStatus
from govapp.apps.catalogue.models.layer_subscriptions import LayerSubscriptionStatus, LayerSubscriptionType

# class CatalogueModelAdmin(reversion.admin.VersionAdmin):
#     ordering = ('id', 'name')
    
def construct_catalogue_entry_link(catalogue_entry):
    return format_html(f'<a href="/admin/catalogue/catalogueentry/{catalogue_entry.id}/change/">{catalogue_entry.name}</a>')

    
class CatalogueEntryPermissionInline(admin.TabularInline):
    model = models.permission.CatalogueEntryPermission
    raw_id_fields = ('user',)

class CatalogueEntryAdmin(reversion.admin.VersionAdmin):
    """Custom Django Admin for Catalogue Entries."""
    # This provides a better interface for `ManyToMany` fields
    # See: https://stackoverflow.com/questions/5385933/a-better-django-admin-manytomany-field-widget
    # filter_horizontal = ["editors"]
    search_fields = ('id', 'name', 'assigned_to__email', 'custodian__name', 'layer_subscription__name',)
    # list_display = ('id', 'name', 'status', 'type', 'permission_type', 'layer_subscription_link','custodian_link', 'assigned_to_link', 'created_at', 'updated_at')
    list_display = ('id', 'name', 'get_status', 'type', 'permission_type', 'layer_subscription_link','custodian_link', 'assigned_to_link', 'created_at', 'updated_at')
    list_filter = ('status', 'type', 'assigned_to', 'custodian', 'permission_type')
    list_display_links = ('id', 'name',)
    ordering = ('id',)
    inlines = [CatalogueEntryPermissionInline]
    raw_id_fields = ('custodian', 'assigned_to')

    class Media:
        css = {'all': ('common/css/admin_custom.css',)}

    def get_status(self, obj):
        if obj.status == CatalogueEntryStatus.NEW_DRAFT:
            return format_html('<span class="badge badge-pill bg-secondary">New Draft</span>')
        elif obj.status == CatalogueEntryStatus.LOCKED:
            return format_html('<span class="badge badge-pill bg-success">Locked</span>')
        elif obj.status == CatalogueEntryStatus.DECLINED:
            return format_html('<span class="badge badge-pill bg-danger">Declined</span>')
        elif obj.status == CatalogueEntryStatus.DRAFT:
            return format_html('<span class="badge badge-pill bg-secondary">Draft</span>')
        elif obj.status == CatalogueEntryStatus.PENDING:
            return format_html('<span class="badge badge-pill bg-warning">Pending</span>')
        else:
            return ''
    get_status.short_description = 'Status'
    
    def custodian_link(self, obj):
        return format_html(f'<a href="/admin/catalogue/custodian/{obj.custodian.id}/change/">{obj.custodian.name}</a>') if obj.custodian else '-'
    custodian_link.short_description = 'Custodian'

    def assigned_to_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.assigned_to.id}/change">{obj.assigned_to}</a>') if obj.assigned_to else '-'
    assigned_to_link.short_description = 'Assigned to'

    def layer_subscription_link(self, obj):
        return format_html(f'<a href="/admin/catalogue/layersubscription/{obj.layer_subscription.id}/change">{obj.layer_subscription}</a>') if obj.layer_subscription else '-'
    layer_subscription_link.short_description = 'Layer Subscription'


class CustodianAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','contact_name','contact_email','contact_phone')
    list_display = ('id', 'name', 'contact_name', 'contact_email', 'contact_phone')
    list_display_links = ('id', 'name',)
    ordering = ('id',)

class LayerAttributeAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'type', 'order', 'catalogue_entry_link')
    list_display_links = ('id', 'name',)
    ordering = ('id',)
    raw_id_fields = ('catalogue_entry',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'

class LayerAttributeTypeAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'key', 'name', 'created_at')
    list_display_links = ('id', 'key',)
    ordering = ('id',)
    
class LayerMetadataAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'catalogue_entry_link','created_at',)
    ordering = ('id',)
    raw_id_fields = ('catalogue_entry',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'
    
class LayerSubmissionAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'catalogue_entry__name', 'file')
    list_display = ('id', 'coloured_status', 'is_active', 'catalogue_entry_link', 'file', 'created_at')
    list_filter = ('status', 'is_active',)
    ordering = ('id',)
    raw_id_fields = ('catalogue_entry',)

    class Media:
        css = {'all': ('common/css/admin_custom.css',)}

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'

    def coloured_status(self, obj):
        if obj.status == LayerSubmissionStatus.SUBMITTED:
            return format_html('<span class="badge badge-pill bg-secondary">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubmissionStatus.ACCEPTED:
            return format_html('<span class="badge badge-pill bg-success">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubmissionStatus.DECLINED:
            return format_html('<span class="badge badge-pill bg-danger">' + obj.get_status_display() + '</span>')
        else:
            return '---'
    coloured_status.short_description = 'Status'


class LayerSubscriptionAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'name', 'description', 'username', 'url', 'host',)
    list_display = ('id', 'name', 'type', 'description', 'get_status', 'enabled', 'workspace_link', 'assigned_to_link', 'username', 'url_link', 'host', 'max_connections', 'min_connections', 'updated_at', 'created_at')
    list_filter = ('enabled', 'type', 'status', 'workspace', 'assigned_to',)
    list_display_links = ('id', 'name',)
    ordering = ('id',)

    class Media:
        css = {'all': ('common/css/admin_custom.css',)}

    def assigned_to_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.assigned_to.id}/change">{obj.assigned_to}</a>') if obj.assigned_to else '-'
    assigned_to_link.short_description = 'Assigned to'

    def url_link(self, obj):
        return format_html(f'<a href="{obj.url}">{obj.url}</a>') if obj.url else ''
    url_link.short_description = 'URL'

    def workspace_link(self, obj):
        return format_html(f'<a href="/admin/publisher/workspace/{obj.workspace.id}/change/">{obj.workspace.name}</a>')
    workspace_link.short_description = 'Workspace'

    def get_status(self, obj):
        if obj.status == LayerSubscriptionStatus.NEW_DRAFT:
            return format_html('<span class="badge badge-pill bg-secondary">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubscriptionStatus.LOCKED:
            return format_html('<span class="badge badge-pill bg-success">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubscriptionStatus.DECLINED:
            return format_html('<span class="badge badge-pill bg-danger">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubscriptionStatus.DRAFT:
            return format_html('<span class="badge badge-pill bg-secondary">' + obj.get_status_display() + '</span>')
        elif obj.status == LayerSubscriptionStatus.PENDING:
            return format_html('<span class="badge badge-pill bg-warning">' + obj.get_status_display() + '</span>')
        else:
            return '---'
    get_status.short_description = 'Status'

    
class LayerSymbologyAdmin(reversion.admin.VersionAdmin):
    search_fields = ('catalogue_entry__id','sld')
    list_display = ('id', 'catalogue_entry_link', 'sld')
    ordering = ('id',)
    raw_id_fields = ('catalogue_entry',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'
    
class EmailNotificationAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','email')
    list_display = ('id', 'name', 'type', 'email', 'active', 'catalogue_entry_link')
    raw_id_fields = ('catalogue_entry',)
    ordering = ('id',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'
    
class WebhookNotificationAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id','name','type', 'url')
    list_display = ('id', 'name', 'type', 'url_link', 'catalogue_entry_link')
    ordering = ('id',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'

    def url_link(self, obj):
        return format_html(f'<a href="{obj.url}">{obj.url}</a>') if obj.url else ''
    url_link.short_description = 'URL'


class CatalogueEntryPermissionAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'catalogue_entry__name',)
    list_display = ('id', 'user_link', 'catalogue_entry_link', 'permission', 'active')
    list_filter = ('active', 'user',)
    raw_id_fields = ('user', 'catalogue_entry',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'

    def user_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.user.id}/change">{obj.user}</a>') if obj.user else '-'
    user_link.short_description = 'User'


class CustomQueryFrequencyAdmin(reversion.admin.VersionAdmin):   
    search_fields = ('id', 'catalogue_entry__name')
    list_display = ('id', 'catalogue_entry_link','last_job_run','type', 'every_minutes','every_hours','hour','minute','day_of_week')
    list_filter = ('type',)

    def catalogue_entry_link(self, obj):
        return construct_catalogue_entry_link(obj.catalogue_entry)
    catalogue_entry_link.short_description = 'Catalogue Entry'


# Register Models
admin.site.register(models.custom_query_frequency.CustomQueryFrequency, CustomQueryFrequencyAdmin)
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
