"""Kaartdijin Boodja Publisher Django Application Administration."""


# Third-Party
from typing import Any
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin, auth
from django.utils.safestring import mark_safe
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
    list_display = ('id', 'name', 'url', 'num_of_layers', 'username', 'enabled', 'created_at')
    ordering = ('id', 'name')

    def num_of_layers(self, obj):
        return f'{obj.total_active_layers} ({obj.total_layers})'

    num_of_layers.short_description = 'active layers (total layers)'


class GeoServerPublishChannelAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'publish_entry', 'geoserver_pool', 'mode', 'frequency', 'workspace', 'active',)
    

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


class GeoServerRolePermissionInline(admin.TabularInline):
    model = models.geoserver_roles_groups.GeoServerRolePermission
    extra = 1  # Number of empty forms to display
    # fields = ['workspace', 'read', 'write', 'admin', 'active']
    fields = ['geoserver_role', 'active', 'read', 'write', 'admin']


class GeoServerGroupRoleInline(admin.TabularInline):
    model = models.geoserver_roles_groups.GeoServerGroupRole
    extra = 1  # Number of empty forms to display
    fields = ['geoserver_role', 'active',]


class GeoServerRoleAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'active', 'created_at',)
    list_display_links = ('id', 'name')
    # inlines = [GeoServerRolePermissionInline,]


class WorkspaceAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'display_geoserver_roles')
    list_display_links = ('id', 'name')
    inlines = [GeoServerRolePermissionInline,]

    def display_geoserver_roles(self, obj):
        geoserver_role_permissions = models.geoserver_roles_groups.GeoServerRolePermission.objects.filter(workspace=obj)
        table_rows = []
        true_icon = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
        false_icon = '<img src="/static/admin/img/icon-no.svg" alt="False">'
        if not geoserver_role_permissions:
            return 'No related geoserver roles found.'
        for index, perm in enumerate(geoserver_role_permissions):
            if index == 0:
                table_rows.append('<tr><th style="width: 25%;text-align: center;">Permission Active</th><th style="">Role Status and Name</th><th style="width: 10%;text-align: center;">Read</th><th style="width: 10%;text-align: center;">Write</th><th style="width: 10%;text-align: center;">Admin</th></tr>')
            perm_active_icon = true_icon if perm.active else false_icon
            role_active_icon = true_icon if perm.geoserver_role.active else false_icon
            role_name = perm.geoserver_role.name
            role_id = perm.geoserver_role.id
            read_icon = true_icon if perm.read else false_icon
            write_icon = true_icon if perm.write else false_icon
            admin_icon = true_icon if perm.admin else false_icon
            table_row = f'<tr><td style="text-align: center;">{perm_active_icon}</td><td>{role_active_icon} <a href="/admin/publisher/geoserverrole/{role_id}/change">{role_name}</a></td><td style="text-align: center;">{read_icon}</td><td style="text-align: center;">{write_icon}</td><td style="text-align: center;">{admin_icon}</td></tr>'
            table_rows.append(table_row)
        table_html = f'<table>{"".join(table_rows)}</table>'
        return mark_safe(table_html)
    display_geoserver_roles.short_description = 'Geoserver Roles and Permissions'

class GeoServerGroupForm(forms.ModelForm):
    # Meta class to specify the model and fields to include in the form
    class Meta:
        model = models.geoserver_roles_groups.GeoServerGroup  # The model associated with this form
        fields = '__all__'  # Include all fields from the GeoServerGroup model

    # A field for selecting multiple GeoServerRole instances
    geoserver_roles = forms.ModelMultipleChoiceField(
        queryset=models.geoserver_roles_groups.GeoServerRole.objects.all(),  # Queryset of GeoServerRole objects to choose from
        required=False,  # This field is optional
        widget=FilteredSelectMultiple(verbose_name='GeoServer Roles', is_stacked=False)  # Use a widget with a filterable multiple select interface
    )


class GeoServerGroupAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'get_geoserver_roles', 'active', 'created_at',)
    list_display_links = ('id', 'name')
    # form = GeoServerGroupForm  # <== This line adds the FilteredSelectMultiple widget.
    inlines = [GeoServerGroupRoleInline,]

    def get_geoserver_roles(self, obj):
        return ','.join([role.name for role in obj.geoserver_roles.all()])
    get_geoserver_roles.short_description = 'roles'

admin.site.register(models.publish_channels.FTPServer, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.FTPPublishChannel, FTPPublishChannelAdmin)
admin.site.register(models.publish_channels.CDDPPublishChannel, reversion.admin.VersionAdmin)
admin.site.register(models.publish_channels.GeoServerPublishChannel, GeoServerPublishChannelAdmin)
admin.site.register(models.publish_entries.PublishEntry, PublishEntryAdmin)
admin.site.register(models.notifications.EmailNotification, reversion.admin.VersionAdmin)
admin.site.register(models.workspaces.Workspace, WorkspaceAdmin)
admin.site.register(models.geoserver_pools.GeoServerPool, GeoServerPoolAdmin)
admin.site.register(models.geoserver_queues.GeoServerQueue, GeoServerQueueAdmin)
admin.site.register(models.geoserver_roles_groups.GeoServerRole, GeoServerRoleAdmin)
admin.site.register(models.geoserver_roles_groups.GeoServerGroup, GeoServerGroupAdmin)
