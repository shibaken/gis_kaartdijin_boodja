"""Kaartdijin Boodja Accounts Django Application Utility Functions."""


# Third-Party
import os
from django import conf
import django
from django.contrib import auth
from django.contrib.auth import models
from django.db.models import query

# Typing
from typing import Iterable, Union

from govapp import settings

import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist


# Configure logging
logger = logging.getLogger(__name__)

# Shortcuts
UserModel = auth.get_user_model()


def all_administrators() -> Iterable[models.User]:
    """Retrieves all of the administrator users.

    Yields:
        models.User: Users in the administrator group.
    """
    # Retrieve and Yield
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_ADMINISTRATORS)
    yield from UserModel.objects.filter(
        # groups__id=conf.settings.GROUP_ADMINISTRATOR_ID
        groups__id=group.id
    )


def all_catalogue_editors() -> Iterable[models.User]:
    """Retrieves all of the administrator users.

    Yields:
        models.User: Users in the administrator group.
    """
    # Retrieve and Yield
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_CATALOGUE_EDITORS)
    yield from UserModel.objects.filter(
        # groups__id=conf.settings.GROUP_CATALOGUE_EDITOR_ID
        groups__id=group.id
    )


def is_administrator(user: Union[models.User, models.AnonymousUser]) -> bool:
    """Checks whether a user is an Administrator.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Administrator group.
    """
    # Check and Return
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_ADMINISTRATORS)
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        # and user.groups.filter(id=conf.settings.GROUP_ADMINISTRATOR_ID).exists()  # Must be in group
        and user.groups.filter(id=group.id).exists()  # Must be in group
    )


def is_catalogue_editor(user: Union[models.User, models.AnonymousUser]) -> bool:
    """Checks whether a user is a Catalogue Editor.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Catalogue Editor group.
    """
    # Check and Return
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_CATALOGUE_EDITORS)
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        # and user.groups.filter(id=conf.settings.GROUP_CATALOGUE_EDITOR_ID).exists()  # Must be in group
        and user.groups.filter(id=group.id).exists()  # Must be in group
    )


def is_catalogue_admin(user: Union[models.User, models.AnonymousUser]) -> bool:
    # Check and Return
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        and user.groups.filter(name=settings.GROUP_CATALOGUE_ADMIN).exists()  # Must be in group
    )


def is_api_user(user: Union[models.User, models.AnonymousUser]) -> bool:
    # Check and Return
    return (
        not isinstance(user, models.AnonymousUser)  # Must be logged in
        and user.groups.filter(name=settings.GROUP_API_USER).exists()  # Must be in group
    )


def limit_to_administrators() -> query.Q:
    """Limits a fields choice to only objects in the Administrators group.

    Returns:
        query.Q: Query to limit object to those in the Administrators group.
    """
    # Construct Query and Return
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_ADMINISTRATORS)
    # return query.Q(groups__pk=conf.settings.GROUP_ADMINISTRATOR_ID)
    return query.Q(groups__pk=group.id)


def limit_to_catalogue_editors() -> query.Q:
    """Limits a fields choice to only objects in the Catalogue Editors group.

    Returns:
        query.Q: Query to limit object to those in the Catalogue Editors group.
    """
    # Construct Query and Return
    group = django.contrib.auth.models.Group.objects.get(name=settings.GROUP_CATALOGUE_EDITORS)
    # return query.Q(groups__pk=conf.settings.GROUP_CATALOGUE_EDITOR_ID)
    return query.Q(groups__pk=group.id)


def hash_password(password):
    """
    Convert Django's hashed password to a GeoServer-compatible format.
    Here we use SHA-256 and Base64 encoding
    """
    try:
        # Assuming password is in Django's 'pbkdf2_sha256' format and removing the scheme
        hashed = password.split('$')[-1]
        return f"crypt1:{hashed}"
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

def generate_users_xml(file_name='dbca-users.xml'):
    """
    Generate the users.xml file from the Django models using a Django template.
    
    :param output_path: Path where the generated users.xml should be saved.
    """
    try:
        from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerGroupUser, GeoServerRole, GeoServerRoleUser
        # Fetch all active users
        users = UserModel.objects.filter(is_active=True)
        
        # Fetch all active groups
        groups = GeoServerGroup.objects.filter(active=True)
        
        # Fetch all active roles
        roles = GeoServerRole.objects.filter(active=True)

        # Prepare user data
        user_data = [{
            'name': user.email,  # Assuming email is used as username
            'password': hash_password(user.password)  # GeoServer needs hashed passwords
        } for user in users]

        # Prepare group data
        group_data = []
        for group in groups:
            members = GeoServerGroupUser.objects.filter(geoserver_group=group).values_list('user__email', flat=True)
            group_data.append({
                'name': group.name,
                'members': list(members)
            })

        # Prepare role data
        role_data = []
        for role in roles:
            users_in_role = GeoServerRoleUser.objects.filter(geoserver_role=role).values_list('user__email', flat=True)
            role_data.append({
                'name': role.name,
                'users': list(users_in_role)
            })

        # Render the template with the data
        rendered_xml = render_to_string('govapp/geoserver/users_template.xml', {
            'users': user_data,
            'groups': group_data,
            'roles': role_data
        })

        # Save the rendered XML to the output path
        save_path = os.path.join(settings.GEOSERVER_SECURITY_FILE_PATH, file_name)
        with open(save_path, 'w', encoding='utf-8') as output_file:
            output_file.write(rendered_xml)
            logger.info(f"File: [{save_path}] has been successfully generated.")

    except ObjectDoesNotExist as e:
        logger.error(f"Database object not found: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while generating {file_name}: {e}")
        raise
