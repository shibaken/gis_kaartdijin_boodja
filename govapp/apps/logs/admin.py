"""Kaartdijin Boodja Logs Django Application Administration."""


# Third-Party
from django.contrib import admin
import reversion.admin

# Local
from govapp.apps.logs import models

class ActionsLogEntryAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'content_type', 'object_id', 'content_object', 'who', 'when', 'what')
    ordering = ('id',)
    
class CommunicationsLogDocumentAdmin(reversion.admin.VersionAdmin):
    list_display = ('id', 'name', 'description', 'uploaded_at', 'entry', 'file', 'user')
    ordering = ('id',)
    
class CommunicationsLogEntry(reversion.admin.VersionAdmin):
    list_display = ('id', 'content_type', 'object_id', 'content_object', 'type', 'to', 'cc', 'fromm', 'subject', 'text', 'user', 'created_at')
    ordering = ('id',)
    

# Register Models
admin.site.register(models.ActionsLogEntry, ActionsLogEntryAdmin)
admin.site.register(models.CommunicationsLogDocument, CommunicationsLogDocumentAdmin)
admin.site.register(models.CommunicationsLogEntry, CommunicationsLogEntry)
