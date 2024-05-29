import json
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

    @staticmethod
    def _add_or_update_rule(rules, key, value):
        """
        Add a new key-value pair to the dictionary. If the key already exists,
        append the new value to the existing value, separated by a comma.

        :param rules: Dictionary to update
        :param key: Key to add or update
        :param value: Value to add or append
        """
        if key in rules:
            # Append the new value to the existing value, separated by a comma
            rules[key] = f"{rules[key]},{value}"
        else:
            # Add the new key-value pair to the dictionary
            rules[key] = value
        
        return rules

    @staticmethod
    def get_rules():
        from django.db.models import Prefetch

        # Prefetch related data to minimize database hits
        permissions = GeoServerRolePermission.objects.filter(active=True).select_related(
            'geoserver_role',
            'workspace'
        ).prefetch_related(
            Prefetch('workspace__publish_channels__publish_entry__catalogue_entry')
        )
        
        rules = {}
        for perm in permissions:
            if perm.workspace:
                # Since we're fetching related objects, ensure they exist
                catalogue_entry = perm.workspace.publish_channels.first().publish_entry.catalogue_entry if perm.workspace.publish_channels.exists() else None
                if catalogue_entry:
                    if perm.read:
                        rules = GeoServerRolePermission._add_or_update_rule(rules, f"{perm.workspace.name}.{catalogue_entry.name}.r", perm.geoserver_role.name)
                    if perm.write:
                        rules = GeoServerRolePermission._add_or_update_rule(rules, f"{perm.workspace.name}.{catalogue_entry.name}.w", perm.geoserver_role.name)
                    if perm.admin:
                        rules = GeoServerRolePermission._add_or_update_rule(rules, f"{perm.workspace.name}.{catalogue_entry.name}.a", perm.geoserver_role.name)
        log.info(f'Rules set in the database: {json.dumps(rules, indent=4)}')
        return rules
