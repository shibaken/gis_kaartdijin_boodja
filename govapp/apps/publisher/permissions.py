"""Kaartdijin Boodja Publisher Django Application Permissions."""


# Third-Party
from rest_framework import permissions
from rest_framework import request
from rest_framework import viewsets

# Local
from govapp.apps.accounts import utils
from govapp.apps.catalogue import models as catalogue_models
from govapp.apps.publisher import models

# Typing
from typing import Any


class IsPublishEntryPermissions(permissions.BasePermission):
    """Permissions for the Publish Entry ViewSet."""

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
            # Check Publish Entry specific permissions
            # 1. Request contains a reference to a Catalogue Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Catalogue Entry's editors
            catalogue_entry = catalogue_models.catalogue_entries.CatalogueEntry.from_request(request)
            allowed = (
                catalogue_entry is not None
                and utils.is_administrator(request.user)
                and catalogue_entry.is_editor(request.user)
            )

        elif view.action in ("destroy", "list", "retrieve", "update", "partial_update",
                             "lock", "unlock", "assign", "unassign", "publish",
                             "publish_cddp", "publish_geoserver"):
            # Retrieves and Lists are always allowed by anyone
            # Updates might be allowed, but we delegate it to `has_object_permission`
            # Locking, Unlocking and Declining might be allowed, but we delegate it to `has_object_permission`
            # Assigning and Unassigning also might be allowed, again we delegate it to `has_object_permission`
            # Manually publishing might be allowed, again we delegate it to `has_object_permission`
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
            # Destroys, Updates and Partial Updates
            # Check Publish Entry specific permissions
            # 1. Object is a Publish Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            # 4. Publish Entry is `assigned_to` this user
            # 5. Publish Entry is unlocked
            allowed = (
                isinstance(obj, models.publish_entries.PublishEntry)
                and utils.is_administrator(request.user)
                and obj.is_editor(request.user)
                and obj.assigned_to == request.user
                and obj.is_unlocked()
            )

        elif view.action in ("lock", "unlock"):
            # Lock, Unlock and Decline
            # 1. Object is a Publish Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            # 4. Publish Entry is `assigned_to` this user
            allowed = (
                isinstance(obj, models.publish_entries.PublishEntry)
                and utils.is_administrator(request.user)
                and obj.is_editor(request.user)
                and obj.assigned_to == request.user
            )

        elif view.action in ("assign", "unassign"):
            # Assign and Unassign
            # Assigning or Unassigning a Publish Entry has its own set of rules
            # 1. Object is a Publish Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            allowed = (
                isinstance(obj, models.publish_entries.PublishEntry)
                and utils.is_administrator(request.user)
                and obj.is_editor(request.user)
            )

        elif view.action in ("publish", "publish_cddp", "publish_geoserver"):
            # Publish
            # Check Publish Entry specific permissions
            # 1. Object is a Publish Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            # 4. Publish Entry is locked
            allowed = (
                isinstance(obj, models.publish_entries.PublishEntry)
                and utils.is_administrator(request.user)
                and obj.is_editor(request.user)
                and obj.is_locked()
            )

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed


class HasPublishEntryPermissions(permissions.BasePermission):
    """Permissions for the Model with a Publish Entry ViewSet."""

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
            # Check Publish Entry specific permissions
            # 1. Request contains a reference to a Publish Entry
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            # 4. Publish Entry is `assigned_to` this user
            # 5. Publish Entry is unlocked
            publish_entry = models.publish_entries.PublishEntry.from_request(request)
            allowed = (
                publish_entry is not None
                and utils.is_administrator(request.user)
                and publish_entry.is_editor(request.user)
                and publish_entry.assigned_to == request.user
                and publish_entry.is_unlocked()
            )

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
            # Check Publish Entry specific permissions
            # 1. Object has a Publish Entry attached to it
            # 2. User is in the Administrators group
            # 3. User is one of this Publish Entry's editors
            # 4. Publish Entry is `assigned_to` this user
            # 5. Publish Entry is unlocked
            allowed = (
                hasattr(obj, "publish_entry")
                and isinstance(obj.publish_entry, models.publish_entries.PublishEntry)
                and utils.is_administrator(request.user)
                and obj.publish_entry.is_editor(request.user)
                and obj.publish_entry.assigned_to == request.user
                and obj.publish_entry.is_unlocked()
            )

        else:
            # Allow all other actions by default
            # This allows dynamically generated actions such as the custom
            # 'choice' actions to be used by anyone
            allowed = True

        # Return
        return allowed
