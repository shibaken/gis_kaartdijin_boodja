import json
import httpx
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroupUser, GeoServerRoleUser

log = logging.getLogger(__name__)
UserModel = get_user_model()
serviceName = 'default'  # Confirm the serviceName at the GeoServer --> [Security] --> [Users, Groups, Roles] --> [Services] tab

class Command(BaseCommand):
    help = 'Synchronize users, roles, and groups with GeoServer.'

    def handle(self, *args, **options):
        geoservers = GeoServerPool.objects.filter(enabled=True)
        for geoserver in geoservers:
            self.sync_users(geoserver)
            self.cleanup_groups(geoserver)
            self.cleanup_roles(geoserver)

    def sync_users(self, geoserver):
        """Synchronize users with GeoServer."""
        log.info(f'Synchronize users in the geoserver: [{geoserver}]...')
        users = UserModel.objects.all()
        for user in users:
            groups = GeoServerGroupUser.objects.filter(user=user)
            roles = GeoServerRoleUser.objects.filter(user=user)
            if groups.exists() or roles.exists():
                self.create_or_update_user(geoserver, user, groups, roles)

    def create_or_update_user(self, geoserver, user, groups, roles):
        """Create or update a user in GeoServer."""
        auth = (geoserver.username, geoserver.password)
        user_data = {
            # "userName": user.email,
            "userName": 'testUserName3',
            "password": "strong_password3",  # Replace with a secure password handling mechanism
            # "enabled": user.is_active
            "enabled": "true"
        }

        response = httpx.get(
            url=f"{geoserver.url}/rest/security/usergroup/service/{serviceName}/users/",
            headers={"Accept": "application/json"},
            auth=auth,
        )
        response.raise_for_status()
        existing_users = response.json()

        # Check if user already exists
        user_exists = any(user_in_geoserver['userName'] == user_data['userName'] for user_in_geoserver in existing_users['users'])

        # Somehow json doesn't work... We use XML formt.
        xml_str = f'<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += f"<user>\n"
        xml_str += f"    <userName>{user_data['userName']}</userName>\n"
        xml_str += f"    <password>{user_data['password']}</password>\n"
        xml_str += f"    <enabled>{str(user_data['enabled']).lower()}</enabled>\n"
        xml_str += f"</user>"

        if user_exists:
            # Update existing user
            response = httpx.post(
                url=f"{geoserver.url}/rest/security/usergroup/service/{serviceName}/user/{user_data['userName']}",
                headers={"Content-Type": "application/xml"},
                content=xml_str,
                # headers={"Content-Type": "application/json"},
                # content=json.dumps(user_data),
                auth=auth
            )
            action = 'updated'
        else:
            # Create new user
            response = httpx.post(
                url=f"{geoserver.url}/rest/security/usergroup/service/{serviceName}/users/",
                headers={"Content-Type": "application/xml"},
                content=xml_str,
                # headers={"Content-Type": "application/json"},
                # content=json.dumps(user_data),
                auth=auth
            )
            action = 'created'

        # Log response
        response.raise_for_status()
        print(f"User: [{user_data['userName']}] has been {action} successfully in GeoServer: [{geoserver}].")

        for group in groups:
            group_url = f"{geoserver.url}/rest/security/usergroup/groups/{group.user_group}/user/{user_data['userName']}"
            httpx.put(
                url=group_url,
                headers={"Content-Type": "application/json"},
                auth=(geoserver.username, geoserver.password),
                timeout=30.0
            )

        for role in roles:
            role_url = f"{geoserver.url}/rest/security/roles/{role.user_role}/users/{user_data['userName']}"
            httpx.put(
                url=role_url,
                headers={"Content-Type": "application/json"},
                auth=(geoserver.username, geoserver.password),
                timeout=30.0
            )

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
