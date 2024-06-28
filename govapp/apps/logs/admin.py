"""Kaartdijin Boodja Logs Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin
from django.utils.html import format_html

# Local
from govapp.apps.logs import models

class ActionsLogEntryAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'what',)
    list_display = ('id', 'content_type', 'object_id', 'content_object_link', 'who_link', 'when', 'what')
    list_filter = ('who', 'content_type',)
    ordering = ('id',)
    
    def who_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.who.id}/change">{obj.who}</a>') if obj.who else '-'
    who_link.short_description = 'Who'

    def content_object_link(self, obj):
        if obj.content_object:
            content_type = obj.content_type
            object_id = obj.object_id
            admin_url = f'/admin/{content_type.app_label}/{content_type.model}/{object_id}/change/'
            return format_html(f'<a href="{admin_url}">{obj.content_object}</a>')
        return '-'
    content_object_link.short_description = 'Content Object'


class CommunicationsLogDocumentAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'name', 'description', )
    list_display = ('id', 'name', 'description', 'entry', 'file', 'user_link', 'uploaded_at')
    list_filter = ('user',)
    ordering = ('id',)

    def user_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.user.id}/change">{obj.user}</a>') if obj.user else '-'
    user_link.short_description = 'User'

    
class CommunicationsLogEntryAdmin(reversion.admin.VersionAdmin):
    search_fields = ('id', 'to', 'cc', 'fromm', 'subject', 'text',)
    list_display = ('id', 'content_type', 'object_id', 'content_object_link', 'type', 'to', 'cc', 'fromm', 'subject', 'text', 'user_link', 'created_at')
    list_filter = ('type', 'user',)
    ordering = ('id',)
    
    def user_link(self, obj):
        return format_html(f'<a href="/admin/auth/user/{obj.user.id}/change">{obj.user}</a>') if obj.user else '-'
    user_link.short_description = 'User'

    def content_object_link(self, obj):
        if obj.content_object:
            content_type = obj.content_type
            object_id = obj.object_id
            admin_url = f'/admin/{content_type.app_label}/{content_type.model}/{object_id}/change/'
            return format_html(f'<a href="{admin_url}">{obj.content_object}</a>')
        return '-'
    content_object_link.short_description = 'Content Object'


# Register Models
admin.site.register(models.ActionsLogEntry, ActionsLogEntryAdmin)
admin.site.register(models.CommunicationsLogDocument, CommunicationsLogDocumentAdmin)
admin.site.register(models.CommunicationsLogEntry, CommunicationsLogEntryAdmin)
