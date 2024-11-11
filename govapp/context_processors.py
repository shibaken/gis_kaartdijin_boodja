"""Context processors for the Django project."""


# Third-Party
from django import conf
from django import http
from django.core.cache import cache

# Typing
from typing import Any

from govapp import settings


def variables(request: http.HttpRequest) -> dict[str, Any]:
    """Constructs a context dictionary to be passed to the templates.

    Args:
        request (http.HttpRequest): HTTP request object.

    Returns:
        dict[str, Any]: Context for the templates.
    """
    # Construct and return context  
    is_django_admin = False
    is_admin = False
    is_catalogue_admin = False

    if request.session.session_key is not None:
        is_django_admin = cache.get('is_django_admin'+ str(request.session.session_key))
        is_admin = cache.get('is_admin'+ str(request.session.session_key))
        is_catalogue_admin = cache.get('is_catalogue_admin' + str(request.session.session_key))
        
        if is_django_admin is None:
            is_django_admin = request.user.groups.filter(name="Django Admin").exists()
            cache.set('is_django_admin'+ str(request.session.session_key), is_django_admin,  86400)
        if is_admin is None:
            is_admin = request.user.groups.filter(name=settings.GROUP_ADMINISTRATORS).exists()
            cache.set('is_admin'+ str(request.session.session_key), is_admin,  86400)
        if is_catalogue_admin is None:
            is_catalogue_admin = request.user.groups.filter(name=settings.GROUP_CATALOGUE_ADMIN).exists()
            cache.set('is_catalogue_admin' + str(request.session.session_key), is_catalogue_admin, 3600)
    
    return {
        "template_group": "kaartdijinboodja",
        "template_title": "",
        "app_build_url": conf.settings.DEV_APP_BUILD_URL,
        "GIT_COMMIT_HASH": conf.settings.GIT_COMMIT_HASH,
        "DJANGO_SETTINGS": conf.settings,
        "settings": conf.settings,
        "is_django_admin": is_django_admin, # request.user.groups.filter(name="Django Admin").exists(),
        "is_admin": is_admin, # request.user.groups.filter(name="Administrators").exists(),
        'is_catalogue_admin': is_catalogue_admin,
        'MANAGEMENT_COMMANDS_PAGE_ENABLED': conf.settings.MANAGEMENT_COMMANDS_PAGE_ENABLED
    }
