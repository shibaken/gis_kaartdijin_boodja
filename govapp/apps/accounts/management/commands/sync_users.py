import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

from govapp import settings
from govapp.apps.accounts.utils import generate_auth_files, generate_role_files, generate_security_config_file, generate_usergroup_files
from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup

log = logging.getLogger(__name__)
UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Synchronize users, roles, and groups with GeoServer.'

    def handle(self, *args, **options):
        geoservers = GeoServerPool.objects.filter(enabled=True)
        for geoserver in geoservers:
            # Sync relations between users and groups, and users and roles
            geoserver.sync_users_groups_users_roles()

            # Sync relations between roles with grous ###
            geoserver.sync_groups_roles()

            # Cleanup users
            geoserver.cleanup_users()
