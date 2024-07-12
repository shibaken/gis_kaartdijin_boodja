import logging

import django

from govapp import settings
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerRole, GeoServerUserGroupService


logger = logging.getLogger(__name__)


class DefaultDataManager(object):

    def __init__(self):
        for group_name in settings.CUSTOM_GROUPS:
            try:
                group, created = django.contrib.auth.models.Group.objects.get_or_create(name=group_name)
                if created:
                    logger.info(f"Created Group: {group_name}")
            except Exception as e:
                logger.error(f'{e}, Group name: {group_name}')

        for role_name in settings.DEFAULT_ROLES_IN_GEOSERVER:
            try:
                role, created = GeoServerRole.objects.get_or_create(name=role_name)
                if created:
                    logger.info(f"Created GeoServerRole: {role_name}")
            except Exception as e:
                logger.error(f'{e}, GeoServerRole name: {role_name}')

        for ug_service_name in settings.GEOSERVER_USERGROUP_SERVICE_NAMES:
            try:
                service_name, created = GeoServerUserGroupService.objects.get_or_create(name=ug_service_name)
                if created:
                    logger.info(f"Created GeoServerUserGroupService: {service_name}")
            except Exception as e:
                logger.error(f'{e}, GeoServerUserGroupService: {service_name}')
