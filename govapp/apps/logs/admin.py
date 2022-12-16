"""Kaartdijin Boodja Logs Django Application Administration."""


# Third-Party
from django.contrib import admin

# Local
from . import models


# Register Models
admin.site.register(models.ActionsLogEntry)
admin.site.register(models.CommunicationsLogDocument)
admin.site.register(models.CommunicationsLogEntry)
