"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from rest_framework import permissions
from rest_framework import request
from rest_framework import viewsets

# Local
from . import models
from . import utils

# Typing
from typing import Any


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
        if view.action in ("create", "delete"):
            # Creates and Deletes are not allowed by anyone
            allowed = False

        elif view.action in ("list", "retrieve", "update", "partial_update", "lock", "unlock"):
            # Retrieves and Lists are always allowed by anyone
            # Updates might be allowed, but we delegate it to `has_object_permission`
            # Locking and Unlocking might be allowed, but we delegate it to `has_object_permission`
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
        if view.action in ("create", "delete"):
            # Creates and Deletes are not allowed by anyone
            allowed = False

        elif view.action in ("list", "retrieve"):
            # Retrieves and Lists are always allowed by anyone
            allowed = True

        elif view.action in ("update", "partial_update"):
            # Update and Partial Update
            # Check Catalogue Entry specific permissions
            # 1. Object is a Catalogue Entry
            # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            allowed = (
                isinstance(obj, models.catalogue_entries.CatalogueEntry)
                and obj.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
                and obj.assigned_to == request.user
                and utils.is_catalogue_editor(request.user)
            )

        elif view.action in ("lock", "unlock"):
            # Lock and Unlock
            # 1. Object is a Catalogue Entry
            # 2. Catalogue Entry is `assigned_to` the request user
            # 3. User is in the Catalogue Editor group
            allowed = (
                isinstance(obj, models.catalogue_entries.CatalogueEntry)
                and obj.assigned_to == request.user
                and utils.is_catalogue_editor(request.user)
            )

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
            # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            catalogue_entry = utils.catalogue_entry_from_request(request)
            allowed = (
                catalogue_entry is not None
                and catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
                and catalogue_entry.assigned_to == request.user
                and utils.is_catalogue_editor(request.user)
            )

        elif view.action in ("delete", "list", "retrieve", "update", "partial_update"):
            # Deletes might be allowed, but we delegate it to `has_object_permission`
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

        elif view.action in ("delete", "update", "partial_update"):
            # Delete, Update and Partial Update
            # Check Catalogue Entry specific permissions
            # 1. Object has a Catalogue Entry attached to it
            # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
            # 3. Catalogue Entry is `assigned_to` the request user
            # 4. User is in the Catalogue Editor group
            allowed = (
                hasattr(obj, "catalogue_entry")
                and isinstance(obj.catalogue_entry, models.catalogue_entries.CatalogueEntry)
                and obj.catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
                and obj.catalogue_entry.assigned_to == request.user
                and utils.is_catalogue_editor(request.user)
            )

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed
