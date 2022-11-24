"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from rest_framework import permissions
from rest_framework import request
from rest_framework import views

# Local
from . import models
from . import utils

# Typing
from typing import Any


class IsCatalogueEntryPermissions(permissions.BasePermission):
    """Permissions for the Catalogue Entry ViewSet."""

    def has_object_permission(self, request: request.Request, view: views.APIView, obj: Any) -> bool:
        """Checks object level permissions.

        Args:
            request (request.Request): Request to check permissions for.
            view (views.APIView): View to check permissions for.
            obj (Any): Object to check permissions for.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check read permissions
        read_is_permitted = request.method in permissions.SAFE_METHODS

        # Check Catalogue Entry specific permissions
        # 1. Object is a Catalogue Entry
        # 2. Catalogue Entry is `assigned_to` the request user
        # 3. The user is in the Catalogue Editor group
        modify_is_permitted = (
            isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and return
        return read_is_permitted or modify_is_permitted


class HasCatalogueEntryPermissions(permissions.BasePermission):
    """Permissions for the Model with a Catalogue Entry ViewSet."""

    def has_permission(self, request: request.Request, view: views.APIView) -> bool:
        """Checks permissions.

        This method is specifically used to check permissions for the `create`
        action, so it is only possible to create a Layer Attribute and add it
        to an existing Catalogue Entry if you have permissions for that
        Catalogue Entry.

        Args:
            request (request.Request): Request to check permissions for.
            view (views.APIView): View to check permissions for.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check method
        if request.method != "POST":
            return True

        # Get Catalogue Entry ID in Request Data
        cid = request.data.get("catalogue_entry")

        # Check Catalogue Entry
        if not cid:
            return True

        # Retrieve Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.filter(id=cid).first()

        # Check Catalogue Entry
        if not catalogue_entry:
            return True

        # Check Catalogue Entry Permissions
        if (
            catalogue_entry.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        ):
            return True

        # Done
        return False

    def has_object_permission(self, request: request.Request, view: views.APIView, obj: Any) -> bool:
        """Checks object level permissions.

        Args:
            request (request.Request): Request to check permissions for.
            view (views.APIView): View to check permissions for.
            obj (Any): Object to check permissions for.

        Returns:
            bool: Whether permission is allowed.
        """
        # Check read permissions
        read_is_permitted = request.method in permissions.SAFE_METHODS

        # Check  specific permissions
        # 1. Object is has a Catalogue Entry attached to it
        # 2. The Catalogue Entry is `assigned_to` the request user
        # 3. The user is in the Catalogue Editor group
        modify_is_permitted = (
            hasattr(obj, "catalogue_entry")
            and isinstance(obj.catalogue_entry, models.catalogue_entries.CatalogueEntry)
            and obj.catalogue_entry.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and return
        return read_is_permitted or modify_is_permitted
