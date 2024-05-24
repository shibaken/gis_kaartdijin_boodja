import logging
import reversion

from django.db import models

from govapp.apps.publisher.models.workspaces import Workspace
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

    def __str__(self) -> str:
        return self.name


class GeoServerGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('geoserver_roles')


@reversion.register()
class GeoServerGroup(mixins.RevisionedMixin):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geoserver_roles = models.ManyToManyField(GeoServerRole, through='GeoServerGroupRole', related_name='geoserver_groups')
    objects = GeoServerGroupManager()

    class Meta:
        verbose_name = "GeoServer Group"
        verbose_name_plural = "GeoServer Groups"

    def __str__(self) -> str:
        return self.name


@reversion.register()
class GeoServerGroupRole(mixins.RevisionedMixin):
    geoserver_group = models.ForeignKey(GeoServerGroup, null=True, blank=True, on_delete=models.CASCADE)
    geoserver_role = models.ForeignKey(GeoServerRole, null=True, blank=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GeoServer GroupRole"
        verbose_name_plural = "GeoServer GroupRoles"
    

@reversion.register()
class GeoServerRolePermission(mixins.RevisionedMixin):
    geoserver_role = models.ForeignKey(GeoServerRole, null=True, blank=True, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, null=True, blank=True, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GeoServer RolePermission"
        verbose_name_plural = "GeoServer RolePermissions"
