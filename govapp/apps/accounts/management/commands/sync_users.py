import logging
import decouple
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from govapp import settings
from govapp.apps.accounts.utils import generate_auth_files, generate_role_files, generate_security_config_file, generate_usergroup_files
from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerGroupUser, GeoServerRole, GeoServerRoleUser

log = logging.getLogger(__name__)
UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Synchronize users, roles, and groups with GeoServer.'

    def handle(self, *args, **options):
        # # Local Storage Paths
        # if not os.path.exists(settings.GEOSERVER_SECURITY_FILE_PATH):
        #     os.makedirs(settings.GEOSERVER_SECURITY_FILE_PATH)

        # # security/config.xml
        # generate_security_config_file(['default', settings.GEOSERVER_CUSTOM_USERGROUP_SERVICE_NAME])

        # # security/auth/config.xml
        # generate_auth_files(settings.GEOSERVER_CUSTOM_AUTHENTICATION_PROVIDER_NAME)

        # # security/usergroup/config.xml
        # # security/usergroup/users.xml
        # # security/usergroup/users.xsd
        # generate_usergroup_files(settings.GEOSERVER_CUSTOM_USERGROUP_SERVICE_NAME, 'users.xml')

        # # security/role/roles.xml
        # generate_role_files()
        # return

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
        user_data = {
            "user": {
                "userName": user.email,
                "password": user.password,  # Replace with a secure password handling mechanism
                "enabled": user.is_active
            }
        }

        # Check if user already exists
        existing_users = geoserver.get_all_users(settings.GEOSERVER_USERGROUP_SERVICE_NAME_CUSTOM)
        user_exists = any(user_in_geoserver['userName'] == user_data['user']['userName'] for user_in_geoserver in existing_users)

        # Create/Update user
        if user_exists:
            log.info(f'User: [{user.email}] exists in the geoserver: [{geoserver}]')
            response = geoserver.update_existing_user(user_data, settings.GEOSERVER_USERGROUP_SERVICE_NAME_CUSTOM)
        else:
            log.info(f'User: [{user.email}] does not exist in the geoserver: [{geoserver}]')
            response = geoserver.create_new_user(user_data, settings.GEOSERVER_USERGROUP_SERVICE_NAME_CUSTOM)

        response.raise_for_status()

    def sync_relations_users_roles(self, geoserver, user):
        roles_for_user_in_kb = geoserver.associate_user_with_roles(user)
        geoserver.disassociate_user_from_roles(user, roles_for_user_in_kb)

    def sync_relations_users_groups(self, geoserver, user):
        groups_for_user_in_kb = geoserver.associate_user_with_groups(user)
        geoserver.disassociate_user_from_groups(user, groups_for_user_in_kb)

    def cleanup_groups(self, geoserver):
        log.info(f'Cleaning up groups in the geoserver: [{geoserver}]...')

        all_groups_in_geoserver = geoserver.get_all_groups(settings.GEOSERVER_USERGROUP_SERVICE_NAME_CUSTOM)
        all_groups_in_kb = GeoServerGroup.objects.all()

        for group_in_geoserver in all_groups_in_geoserver:
            group_exists_in_kb = any(group_in_geoserver == group_in_kb.name for group_in_kb in all_groups_in_kb)

            if not group_exists_in_kb and group_exists_in_kb not in settings.NON_DELETABLE_USERGROUPS:
                log.info(f'Group: [{group_in_geoserver}] exists in the geoserver: [{geoserver}], but not in KB.')
                geoserver.delete_existing_group(group_in_geoserver, settings.GEOSERVER_USERGROUP_SERVICE_NAME_CUSTOM)

    def cleanup_roles(self, geoserver):
        log.info(f'Cleaning up roles in the geoserver: [{geoserver}]...')

        all_roles_in_geoserver = geoserver.get_all_roles()
        all_roles_in_kb = GeoServerRole.objects.all()

        for role_in_geoserver in all_roles_in_geoserver:
            role_exists_in_kb = any(role_in_geoserver == role_in_kb.name for role_in_kb in all_roles_in_kb)

            if not role_exists_in_kb and role_exists_in_kb not in settings.NON_DELETABLE_ROLES and role_exists_in_kb not in settings.DEFAULT_ROLES_IN_GEOSERVER:
                log.info(f'Role: [{role_in_geoserver}] exists in the geoserver: [{geoserver}], but not in KB.')
                geoserver.delete_existing_role(role_in_geoserver)
