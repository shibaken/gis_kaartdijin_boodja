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


@reversion.register()
class GeoServerGroup(mixins.RevisionedMixin):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geoserver_roles = models.ManyToManyField(GeoServerRole, through='GeoServerGroupRole', related_name='geoserver_groups')

    class Meta:
        verbose_name = "GeoServer Group"
        verbose_name_plural = "GeoServer Groups"


@reversion.register()
class GeoServerGroupRole(mixins.RevisionedMixin):
    geoserver_group = models.ForeignKey(GeoServerGroup, null=True, blank=True, on_delete=models.CASCADE)
    geoserver_role = models.ForeignKey(GeoServerRole, null=True, blank=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GeoServer Role"
        verbose_name_plural = "GeoServer Roles"


