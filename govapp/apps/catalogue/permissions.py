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
        # Create and Delete
        # Creates and Deletes are not allowed by anyone
        create_and_delete = False

        # Retrieve and List
        # Retrieves and Lists are always allowed by anyone
        retrieve_and_list = view.action in ("list", "retrieve")

        # Update and Partial Update
        # Updates might be allowed, but we delegate it to `has_object_permission`
        update_and_partial_update = view.action in ("update", "partial_update")

        # Lock and Unlock
        # Locking and Unlocking might be allowed, but we delegate it to `has_object_permission`
        lock_and_unlock = view.action in ("lock", "unlock")

        # Check permissions and Return
        return (
            create_and_delete
            or retrieve_and_list
            or update_and_partial_update
            or lock_and_unlock
        )

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
        # Create and Delete
        # Creates and Deletes are not allowed by anyone
        create_and_delete = False

        # Retrieve and List
        # Retrieves and Lists are always allowed by anyone
        retrieve_and_list = view.action in ("list", "retrieve")

        # Update and Partial Update
        # Check Catalogue Entry specific permissions
        # 1. Object is a Catalogue Entry
        # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 3. Catalogue Entry is `assigned_to` the request user
        # 4. User is in the Catalogue Editor group
        update_and_partial_update = (
            view.action in ("update", "partial_update")
            and isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and obj.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Lock and Unlock
        # 1. Object is a Catalogue Entry
        # 2. Catalogue Entry is `assigned_to` the request user
        # 3. User is in the Catalogue Editor group
        lock_and_unlock = (
            view.action in ("lock", "unlock")
            and isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and Return
        return (
            create_and_delete
            or retrieve_and_list
            or update_and_partial_update
            or lock_and_unlock
        )


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
        # Create
        # Check Catalogue Entry specific permissions
        # 1. Request contains a reference to a Catalogue Entry
        # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 3. Catalogue Entry is `assigned_to` the request user
        # 4. User is in the Catalogue Editor group
        catalogue_entry = utils.catalogue_entry_from_request(request)
        create = (
            view.action == "create"
            and catalogue_entry is not None
            and catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and catalogue_entry.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Delete
        # Deletes might be allowed, but we delegate it to `has_object_permission`
        delete = view.action == "delete"

        # Retrieve and List
        # Retrieves and Lists are always allowed by anyone
        retrieve_and_list = view.action in ("list", "retrieve")

        # Update and Partial Update
        # Updates might be allowed, but we delegate it to `has_object_permission`
        update_and_partial_update = view.action in ("update", "partial_update")

        # Check permissions and Return
        return (
            create
            or delete
            or retrieve_and_list
            or update_and_partial_update
        )

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
        # Retrieve and List
        # Retrieves and Lists are always allowed by anyone
        retrieve_and_list = view.action in ("list", "retrieve")

        # Update and Partial Update
        # Check Catalogue Entry specific permissions
        # 1. Object has a Catalogue Entry attached to it
        # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 3. Catalogue Entry is `assigned_to` the request user
        # 4. User is in the Catalogue Editor group
        update_and_partial_update_and_delete = (
            view.action in ("update", "partial_update", "delete")
            and hasattr(obj, "catalogue_entry")
            and isinstance(obj.catalogue_entry, models.catalogue_entries.CatalogueEntry)
            and obj.catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and obj.catalogue_entry.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and Return
        return (
            retrieve_and_list
            or update_and_partial_update_and_delete
        )
