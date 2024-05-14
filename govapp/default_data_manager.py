import logging

import django

from govapp import settings


logger = logging.getLogger(__name__)


class DefaultDataManager(object):

    def __init__(self):
        for group_name in settings.CUSTOM_GROUPS:
            try:
                group, created = django.contrib.auth.models.Group.objects.get_or_create(name=group_name)
                if created:
                    logger.info("Created Group: {}".format(group_name))
            except Exception as e:
                logger.error('{}, Group name: {}'.format(e, group_name))