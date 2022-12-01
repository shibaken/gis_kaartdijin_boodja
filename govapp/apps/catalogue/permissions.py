"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django import conf
from django.contrib.auth import models as auth_models
from rest_framework import permissions
from rest_framework import request
from rest_framework import viewsets

# Local
from . import models

# Typing
from typing import Any, Optional, Union


class IsCatalogueEntryPermissions(permissions.BasePermission):
    """Permissions for the Catalogue Entry ViewSet."""

    def has_permission(  # type: ignore
        self,
        request: request.Request,
        view: viewsets.GenericViewSet,
    ) -> bool:
        """Checks viewset request level permissions.

        Args:
            request (request.Request): Request to check permissions.
            view (viewsets.GenericViewSet): Viewset to check permissions.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check Action
        if view.action in ("create", "destroy"):
            # Creates and Destroys are not allowed by anyone
            allowed = False

        elif view.action in ("list", "retrieve", "update", "partial_update", "lock", "unlock", "decline"):
            # Retrieves and Lists are always allowed by anyone
            # Updates might be allowed, but we delegate it to `has_object_permission`
            # Locking, Unlocking and Declining might be allowed, but we delegate it to `has_object_permission`
            allowed = True

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed

    def has_object_permission(  # type: ignore
        self,
        request: request.Request,
        view: viewsets.GenericViewSet,
        obj: Any,
    ) -> bool:
        """Checks object level permissions.

        Args:
            request (request.Request): Request to check permissions.
            view (viewsets.GenericViewSet): Viewset to check permissions.
            obj (Any): Object to check permissions.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check Action
        if view.action in ("create", "destroy"):
            # Creates and Destroys are not allowed by anyone
            allowed = False

        elif view.action in ("list", "retrieve"):
            # Retrieves and Lists are always allowed by anyone
            allowed = True

        elif view.action in ("update", "partial_update"):
            # Update and Partial Update
            # Check Catalogue Entry specific permissions
            # 1. Object is a Catalogue Entry
            # 2. Catalogue Entry is unlocked
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            allowed = (
                isinstance(obj, models.catalogue_entries.CatalogueEntry)
                and obj.is_unlocked()
                and obj.assigned_to == request.user
                and is_catalogue_editor(request.user)
            ) or is_administrator(request.user)

        elif view.action in ("lock", "unlock", "decline"):
            # Lock, Unlock and Decline
            # 1. Object is a Catalogue Entry
            # 2. Catalogue Entry is `assigned_to` the request user
            # 3. User is in the Catalogue Editor group
            allowed = (
                isinstance(obj, models.catalogue_entries.CatalogueEntry)
                and obj.assigned_to == request.user
                and is_catalogue_editor(request.user)
            ) or is_administrator(request.user)

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed


class HasCatalogueEntryPermissions(permissions.BasePermission):
    """Permissions for the Model with a Catalogue Entry ViewSet."""

    def has_permission(  # type: ignore
        self,
        request: request.Request,
        view: viewsets.GenericViewSet,
    ) -> bool:
        """Checks viewset request level permissions.

        Args:
            request (request.Request): Request to check permissions.
            view (viewsets.GenericViewSet): Viewset to check permissions.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check Action
        if view.action == "create":
            # Create
            # Check Catalogue Entry specific permissions
            # 1. Request contains a reference to a Catalogue Entry
            # 2. Catalogue Entry is unlocked
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            catalogue_entry = catalogue_entry_from_request(request)
            allowed = (
                catalogue_entry is not None
                and catalogue_entry.is_unlocked()
                and catalogue_entry.assigned_to == request.user
                and is_catalogue_editor(request.user)
            ) or is_administrator(request.user)

        elif view.action in ("destroy", "list", "retrieve", "update", "partial_update"):
            # Destroys might be allowed, but we delegate it to `has_object_permission`
            # Retrieves and Lists are always allowed by anyone
            # Updates might be allowed, but we delegate it to `has_object_permission`
            allowed = True

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed

    def has_object_permission(  # type: ignore
        self,
        request: request.Request,
        view: viewsets.GenericViewSet,
        obj: Any,
    ) -> bool:
        """Checks object level permissions.

        Args:
            request (request.Request): Request to check permissions.
            view (viewsets.GenericViewSet): Viewset to check permissions.
            obj (Any): Object to check permissions.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check Action
        if view.action in ("list", "retrieve"):
            # Retrieves and Lists are always allowed by anyone
            allowed = True

        elif view.action in ("destroy", "update", "partial_update"):
            # Destroy, Update and Partial Update
            # Check Catalogue Entry specific permissions
            # 1. Object has a Catalogue Entry attached to it
            # 2. Catalogue Entry is unlocked
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            allowed = (
                hasattr(obj, "catalogue_entry")
                and isinstance(obj.catalogue_entry, models.catalogue_entries.CatalogueEntry)
                and obj.catalogue_entry.is_unlocked()
                and obj.catalogue_entry.assigned_to == request.user
                and is_catalogue_editor(request.user)
            ) or is_administrator(request.user)

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed


def is_administrator(user: Union[auth_models.User, auth_models.AnonymousUser]) -> bool:
    """Checks whether a user is an Administrator.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Administrator group.
    """
    # Check and Return
    return (
        not isinstance(user, auth_models.AnonymousUser)  # Must be logged in
        and user.groups.filter(id=conf.settings.GROUP_ADMINISTRATOR_ID).exists()  # Must be in group
    )


def is_catalogue_editor(user: Union[auth_models.User, auth_models.AnonymousUser]) -> bool:
    """Checks whether a user is a Catalogue Editor.

    Args:
        user (Union[models.User, models.AnonymousUser]): User to be checked.

    Returns:
        bool: Whether the user is in the Catalogue Editor group.
    """
    # Check and Return
    return (
        not isinstance(user, auth_models.AnonymousUser)  # Must be logged in
        and user.groups.filter(id=conf.settings.GROUP_CATALOGUE_EDITOR_ID).exists()  # Must be in group
    )


def catalogue_entry_from_request(request: request.Request) -> Optional[models.catalogue_entries.CatalogueEntry]:
    """Retrieves a possible Catalogue Entry from request data.

    Args:
        request (request.Request): Request to retrieve Catalogue Entry from.

    Returns:
        Optional[models.catalogue_entries.CatalogueEntry]: Catalogue Entry.
    """
    # Retrieve Possible Catalogue Entry and Return
    return models.catalogue_entries.CatalogueEntry.objects.filter(
        id=request.data.get("catalogue_entry", -1),  # -1 Sentinel Value for Non-Existent Catalogue Entry
    ).first()
