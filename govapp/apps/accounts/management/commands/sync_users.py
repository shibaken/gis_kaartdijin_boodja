import json
import httpx
import logging
import urllib.parse
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerGroupRole, GeoServerGroupUser, GeoServerRoleUser

log = logging.getLogger(__name__)
UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Synchronize users, roles, and groups with GeoServer.'
    USE_EMAIL_AS_USERNAME = False  # For now, set to False

    def handle(self, *args, **options):
        geoservers = GeoServerPool.objects.filter(enabled=True)
        for geoserver in geoservers:
            # Sync relations between users and groups, and users and roles
            self.sync_users_groups_roles(geoserver)

            # Sync relations between roles with grous ###
            self.sync_groups_roles(geoserver)

            # Cleanup
            self.cleanup_groups(geoserver)
            self.cleanup_roles(geoserver)

    def sync_groups_roles(self, geoserver):
        """Synchronize groups-roles with GeoServer."""
        log.info(f'Synchronize groups-roles in the geoserver: [{geoserver}]...')

        geoserver_groups_in_kb = GeoServerGroup.objects.all()
        for geoserver_group_in_kb in geoserver_groups_in_kb:
            self.sync_relations_groups_roles(geoserver, geoserver_group_in_kb)

    def sync_relations_groups_roles(self, geoserver, geoserver_group_in_kb):
        # Associate group with roles
        roles_in_geoserver = geoserver.get_all_roles_for_group(geoserver_group_in_kb.name)
        for geoserver_role_in_kb in geoserver_group_in_kb.geoserver_roles.all():
            role_exists = any(geoserver_role_in_kb.name == role_in_geoserver for role_in_geoserver in roles_in_geoserver)
            if not role_exists:
                geoserver.create_new_role(geoserver_role_in_kb.name)
            geoserver.associate_role_with_group(geoserver_role_in_kb.name, geoserver_group_in_kb.name)

        # Disassociate group from roles
        for role_in_geoserver in roles_in_geoserver:
            role_exists = any(role_in_geoserver == geoserver_role_in_kb.name for geoserver_role_in_kb in geoserver_group_in_kb.geoserver_roles.all())
            if not role_exists:
                geoserver.disassociate_role_from_group(role_in_geoserver, geoserver_group_in_kb.name)

    def sync_users_groups_roles(self, geoserver):
        """Synchronize users-groups and users-roles with GeoServer."""
        log.info(f'Synchronize users-groups and users-roles in the geoserver: [{geoserver}]...')
        users = UserModel.objects.all()
        for user in users:
            self.create_or_update_user(geoserver, user)

            # Sync relations between users and groups
            self.sync_relations_users_groups(geoserver, user)

            # Sync relations between users and roles
            self.sync_relations_users_roles(geoserver, user)

    def create_or_update_user(self, geoserver, user):
        """Create or update a user in GeoServer."""
        username = user.email if self.USE_EMAIL_AS_USERNAME else user.username
        
        user_data = {
            "user": {
                "userName": username,
                "password": user.password,  # Replace with a secure password handling mechanism
                "enabled": user.is_active
            }
        }

        # Check if user already exists
        existing_users = geoserver.get_all_users()
        user_exists = any(user_in_geoserver['userName'] == user_data['user']['userName'] for user_in_geoserver in existing_users)

        # Create/Update user
        response = geoserver.update_existing_user(user_data) if user_exists else geoserver.create_new_user(user_data)
        response.raise_for_status()

    def sync_relations_users_roles(self, geoserver, user):
        username = user.email if self.USE_EMAIL_AS_USERNAME else user.username
        roles_in_geoserver = geoserver.get_all_roles_for_user(username)

        # Associate role with user
        roleusers_for_user = GeoServerRoleUser.objects.filter(user=user)
        for roleuser in roleusers_for_user:
            role_in_kb = roleuser.geoserver_role.name
            role_exists = any(role_in_kb == role_in_geoserver for role_in_geoserver in roles_in_geoserver)
            if not role_exists:
                geoserver.create_new_role(role_in_kb)
            geoserver.associate_role_with_user(username, role_in_kb)

        # Disassociate role from user
        for role_in_geoserver in roles_in_geoserver:
            role_exists = any(role_in_geoserver == roleuser.geoserver_role.name for roleuser in roleusers_for_user)
            if not role_exists:
                geoserver.disassociate_role_from_user(username, role_in_geoserver)

    def sync_relations_users_groups(self, geoserver, user):
        username = user.email if self.USE_EMAIL_AS_USERNAME else user.username
        groups_in_geoserver = geoserver.get_all_groups_for_user(username)

        # Associate user with group
        groupusers_for_user = GeoServerGroupUser.objects.filter(user=user)
        for groupuser in groupusers_for_user:
            group_in_kb = groupuser.geoserver_group.name
            group_exists = any(group_in_kb == group_in_geoserver for group_in_geoserver in groups_in_geoserver)
            if not group_exists:
                geoserver.create_new_group(group_in_kb)
            geoserver.associate_user_with_group(username, group_in_kb)

        # Disassociate user from group
        for group_in_geoserver in groups_in_geoserver:
            group_exists = any(group_in_geoserver == groupuser.geoserver_group.name for groupuser in groupusers_for_user)
            if not group_exists:
                geoserver.disassociate_user_from_group(username, group_in_geoserver)


    def cleanup_groups(self, geoserver):
        """Remove groups from users in GeoServer if not assigned."""
        assigned_groups = GeoServerGroupUser.objects.values_list('user_group', flat=True).distinct()
        groups_url = f"{geoserver.url}/rest/security/usergroup/groups"
        response = httpx.get(
            url=groups_url,
            headers={"Accept": "application/json"},
            auth=(geoserver.username, geoserver.password),
            timeout=30.0
        )
        response.raise_for_status()
        groups = response.json().get("groupList", [])

        for group in groups:
            group_name = group["groupName"]
            if group_name not in assigned_groups:
                group_url = f"{geoserver.url}/rest/security/usergroup/groups/{group_name}"
                httpx.delete(
                    url=group_url,
                    headers={"Content-Type": "application/json"},
                    auth=(geoserver.username, geoserver.password),
                    timeout=30.0
                )

    def cleanup_roles(self, geoserver):
        """Remove roles from users in GeoServer if not assigned."""
        assigned_roles = GeoServerRoleUser.objects.values_list('user_role', flat=True).distinct()
        roles_url = f"{geoserver.url}/rest/security/roles"
        response = httpx.get(
            url=roles_url,
            headers={"Accept": "application/json"},
            auth=(geoserver.username, geoserver.password),
            timeout=30.0
        )
        response.raise_for_status()
        roles = response.json().get("roleList", [])

        for role in roles:
            role_name = role["roleName"]
            if role_name not in assigned_roles:
                role_url = f"{geoserver.url}/rest/security/roles/{role_name}"
                httpx.delete(
                    url=role_url,
                    headers={"Content-Type": "application/json"},
                    auth=(geoserver.username, geoserver.password),
                    timeout=30.0
                )
