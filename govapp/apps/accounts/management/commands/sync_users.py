import logging
import decouple
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from govapp import settings
from govapp.apps.accounts.utils import generate_auth_files, generate_role_files, generate_usergroup_files
from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerGroupUser, GeoServerRole, GeoServerRoleUser

log = logging.getLogger(__name__)
UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Synchronize users, roles, and groups with GeoServer.'
    USE_EMAIL_AS_USERNAME = True  # For now, set to False

    def handle(self, *args, **options):
        # Local Storage Paths
        if not os.path.exists(settings.GEOSERVER_SECURITY_FILE_PATH):
            os.makedirs(settings.GEOSERVER_SECURITY_FILE_PATH)

        ### TEST ###
        generate_auth_files(settings.GEOSERVER_CUSTOM_AUTHENTICATION_PROVIDER_NAME)
        generate_usergroup_files(settings.GEOSERVER_CUSTOM_USERGROUP_SERVICE_NAME, 'users.xml')
        generate_role_files()
        return

        geoservers = GeoServerPool.objects.filter(enabled=True)
        for geoserver in geoservers:
            # Sync relations between users and groups, and users and roles
            self.sync_users_groups_roles(geoserver)

            # Sync relations between roles with groups ###
            self.sync_groups_roles(geoserver)

            # Cleanup
            self.cleanup_groups(geoserver)
            self.cleanup_roles(geoserver)

    def sync_groups_roles(self, geoserver):
        """Synchronize groups-roles with GeoServer."""
        log.info(f'Synchronize groups-roles in the geoserver: [{geoserver}]...')

        groups_in_kb = GeoServerGroup.objects.all()
        log.info(f'Group(s): [{groups_in_kb}] found in the KB.')

        for group_in_kb in groups_in_kb:
            self.sync_relations_groups_roles(geoserver, group_in_kb)

    def sync_relations_groups_roles(self, geoserver, group_in_kb):
        # Associate group with roles
        roles_for_group_in_kb = group_in_kb.geoserver_roles.all()
        log.info(f'Role(s): [{roles_for_group_in_kb}] for the group: [{group_in_kb.name}] found in the KB')

        all_roles_in_geoserver = geoserver.get_all_roles()
        log.info(f'Role(s): [{all_roles_in_geoserver}] found in the geoserver: [{geoserver}].')

        roles_for_group_in_geoserver = geoserver.get_all_roles_for_group(group_in_kb.name)
        log.info(f'Role(s): [{roles_for_group_in_geoserver}] found for the group: [{group_in_kb.name}] in the geoserver: [{geoserver}].')

        for role_in_kb in roles_for_group_in_kb:
            role_associated = any(role_in_kb.name == role_in_geoserver for role_in_geoserver in roles_for_group_in_geoserver)
            if role_associated:
                log.info(f'Role: [{role_in_kb.name}] is already associated with the group: [{group_in_kb.name}] in the geoserver: [{geoserver}].')
            else:
                log.info(f'Role: [{role_in_kb.name}] is not associated with the group: [{group_in_kb.name}] in the geoserver: [{geoserver}].')
                role_exists = any(role_in_kb.name == role_in_geoserver for role_in_geoserver in all_roles_in_geoserver)
                if not role_exists:
                    log.info(f'Role: [{role_in_kb.name}] does not exist in the geoserver: [{geoserver}].')
                    geoserver.create_new_role(role_in_kb.name)
                geoserver.associate_role_with_group(role_in_kb.name, group_in_kb.name)

        # Disassociate group from roles
        all_roles_in_geoserver = geoserver.get_all_roles()
        log.info(f'Role(s): [{all_roles_in_geoserver}] found in the geoserver: [{geoserver}].')

        roles_for_group_in_geoserver = geoserver.get_all_roles_for_group(group_in_kb.name)  # Update list
        log.info(f'Role(s): [{roles_for_group_in_geoserver}] found for the group: [{group_in_kb.name}] in the geoserver: [{geoserver}].')

        for role_in_geoserver in roles_for_group_in_geoserver:
            role_associated = any(role_in_geoserver == role_in_kb.name for role_in_kb in roles_for_group_in_kb)
            if not role_associated:
                log.info(f'Role: [{role_in_geoserver}] is associated with the group: [{group_in_kb.name}] in the geoserver: [{geoserver}], but not in KB')
                geoserver.disassociate_role_from_group(role_in_geoserver, group_in_kb.name)

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
        if user_exists:
            log.info(f'User: [{username}] exists in the geoserver: [{geoserver}]')
            response = geoserver.update_existing_user(user_data)
        else:
            log.info(f'User: [{username}] does not exist in the geoserver: [{geoserver}]')
            response = geoserver.create_new_user(user_data)

        response.raise_for_status()

    def sync_relations_users_roles(self, geoserver, user):
        username = user.email if self.USE_EMAIL_AS_USERNAME else user.username

        # Associate role with user
        role_user_in_kb = GeoServerRoleUser.objects.filter(user=user)
        roles_for_user_in_kb = [obj.geoserver_role for obj in role_user_in_kb]
        log.info(f'Role(s): [{roles_for_user_in_kb}] found for the user: [{username}] in the geoserver: [{geoserver}].')

        all_roles_in_geoserver = geoserver.get_all_roles()
        log.info(f'Role(s): [{all_roles_in_geoserver}] found in the geoserver: [{geoserver}].')

        roles_for_user_in_geoserver = geoserver.get_all_roles_for_user(username)
        log.info(f'Role(s): [{roles_for_user_in_geoserver}] for the user: [{username}] found in the geoserver: [{geoserver}].')

        for role_in_kb in roles_for_user_in_kb:
            role_associated = any(role_in_kb.name == role_in_geoserver for role_in_geoserver in roles_for_user_in_geoserver)
            if role_associated:
                log.info(f'Role: [{role_in_kb.name}] is already associated with the user: [{username}] in the geoserver: [{geoserver}].')
            else:
                log.info(f'Role: [{role_in_kb.name}] is not associated with the user: [{username}] in the geoserver: [{geoserver}].')
                role_exists = any(role_in_kb.name == role_in_geoserver for role_in_geoserver in all_roles_in_geoserver)
                if not role_exists:
                    log.info(f'Role: [{role_in_kb.name}] does not exist in the geoserver: [{geoserver}].')
                    geoserver.create_new_role(role_in_kb.name)
                geoserver.associate_role_with_user(username, role_in_kb.name)

        # Disassociate role from user
        all_roles_in_geoserver = geoserver.get_all_roles()
        log.info(f'Role(s): [{all_roles_in_geoserver}] found in the geoserver: [{geoserver}].')

        roles_for_user_in_geoserver = geoserver.get_all_roles_for_user(username)
        log.info(f'Role(s): [{roles_for_user_in_geoserver}] found for the user: [{username}] in the geoserver: [{geoserver}].')

        for role_in_geoserver in roles_for_user_in_geoserver:
            role_associated = any(role_in_geoserver == role_in_kb.name for role_in_kb in roles_for_user_in_kb)
            if not role_associated:
                log.info(f'Role: [{role_in_geoserver}] is associated with the user: [{username}] in the geoserver: [{geoserver}], but not in KB')
                geoserver.disassociate_role_from_user(username, role_in_geoserver)

    def sync_relations_users_groups(self, geoserver, user):
        username = user.email if self.USE_EMAIL_AS_USERNAME else user.username

        # Associate user with group
        group_user_in_kb = GeoServerGroupUser.objects.filter(user=user)
        groups_for_user_in_kb = [obj.geoserver_group for obj in group_user_in_kb]
        log.info(f'Group(s): [{groups_for_user_in_kb}] found for the user: [{username}] in the KB')

        all_groups_in_geoserver = geoserver.get_all_groups()
        log.info(f'Group(s): [{all_groups_in_geoserver}] found in the geoserver: [{geoserver}].')

        groups_for_user_in_geoserver = geoserver.get_all_groups_for_user(username)
        log.info(f'Group(s): [{groups_for_user_in_geoserver}] for the user: [{username}] found in the geoserver: [{geoserver}].')

        for group_in_kb in groups_for_user_in_kb:
            group_associated = any(group_in_kb.name == group_in_geoserver for group_in_geoserver in groups_for_user_in_geoserver)
            if group_associated:
                log.info(f'Group: [{group_in_kb.name}] is already associated with the user: [{username}] in the geoserver: [{geoserver}].')
            else:
                log.info(f'Group: [{group_in_kb.name}] is not associated with the user: [{username}] in the geoserver: [{geoserver}].')
                group_exists = any(group_in_kb.name == group_in_geoserver for group_in_geoserver in all_groups_in_geoserver)
                if not group_exists:
                    log.info(f'Group: [{group_in_kb.name}] does not exist in the geoserver: [{geoserver}].')
                    geoserver.create_new_group(group_in_kb.name)
                geoserver.associate_user_with_group(username, group_in_kb.name)

        # Disassociate user from group
        all_groups_in_geoserver = geoserver.get_all_groups()
        log.info(f'Group(s): [{all_groups_in_geoserver}] found in the geoserver: [{geoserver}].')

        groups_for_user_in_geoserver = geoserver.get_all_groups_for_user(username)
        log.info(f'Group(s): [{groups_for_user_in_geoserver}] for the user: [{username}] found in the geoserver: [{geoserver}].')

        for group_in_geoserver in groups_for_user_in_geoserver:
            group_associated = any(group_in_geoserver == group_in_kb.name for group_in_kb in groups_for_user_in_kb)
            if not group_associated:
                log.info(f'Group: [{group_in_geoserver}] is associated with the user: [{username}] in the geoserver: [{geoserver}], but not in KB')
                geoserver.disassociate_user_from_group(username, group_in_geoserver)

    def cleanup_groups(self, geoserver):
        log.info(f'Cleaning up groups in the geoserver: [{geoserver}]...')

        all_groups_in_geoserver = geoserver.get_all_groups()
        all_groups_in_kb = GeoServerGroup.objects.all()

        for group_in_geoserver in all_groups_in_geoserver:
            group_exists_in_kb = any(group_in_geoserver == group_in_kb.name for group_in_kb in all_groups_in_kb)

            if not group_exists_in_kb and group_exists_in_kb not in settings.NON_DELETABLE_USERGROUPS:
                log.info(f'Group: [{group_in_geoserver}] exists in the geoserver: [{geoserver}], but not in KB.')
                geoserver.delete_existing_group(group_in_geoserver)

    def cleanup_roles(self, geoserver):
        log.info(f'Cleaning up roles in the geoserver: [{geoserver}]...')

        all_roles_in_geoserver = geoserver.get_all_groups()
        all_roles_in_kb = GeoServerRole.objects.all()

        for role_in_geoserver in all_roles_in_geoserver:
            role_exists_in_kb = any(role_in_geoserver == role_in_kb.name for role_in_kb in all_roles_in_kb)

            if not role_exists_in_kb and role_exists_in_kb not in settings.NON_DELETABLE_ROLES and role_exists_in_kb not in settings.DEFAULT_ROLES_IN_GEOSERVER:
                log.info(f'Role: [{role_in_geoserver}] exists in the geoserver: [{geoserver}], but not in KB.')
                geoserver.delete_existing_role(role_in_geoserver)
