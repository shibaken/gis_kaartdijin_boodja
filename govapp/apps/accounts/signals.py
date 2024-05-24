import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib import auth
from django.core.cache import cache


UserModel = auth.get_user_model()
log = logging.getLogger(__name__)


@receiver(post_save, sender=UserModel)
def user_post_save(sender, instance, **kwargs):
    log.debug(f'TODO: We want to delete Group related cache here...')