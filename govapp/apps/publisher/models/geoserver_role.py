import logging
import reversion

from django.db import models

from govapp.common import mixins


# Logging
log = logging.getLogger(__name__)


@reversion.register()
class GeoServerRole(mixins.RevisionedMixin):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GeoServer Role"
        verbose_name_plural = "GeoServer Roles"

