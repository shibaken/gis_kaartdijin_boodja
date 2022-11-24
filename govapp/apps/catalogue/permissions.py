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

        # Check Catalogue Entry specific write permissions
        # This might seem strange, but we allow `POST` requests without the
        # `status` of "DRAFT", as these requests actually control the status.
        # 1. Object is a Catalogue Entry
        # 2. Catalogue Entry is `assigned_to` the request user
        # 3. User is in the Catalogue Editor group
        write_is_permitted = (
            request.method == "POST"
            and isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check Catalogue Entry specific update permissions
        # 1. Object is a Catalogue Entry
        # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 3. Catalogue Entry is `assigned_to` the request user
        # 4. User is in the Catalogue Editor group
        modify_is_permitted = (
            request.method in ("PATCH", "PUT")
            and isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and obj.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and return
        return read_is_permitted or write_is_permitted or modify_is_permitted


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
        # 1. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 2. Catalogue Entry is `assigned_to` the request user
        # 3. User is in the Catalogue Editor group
        if (
            catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and catalogue_entry.assigned_to == request.user
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
        # 1. Object has a Catalogue Entry attached to it
        # 2. Catalogue Entry is unlocked (i.e., status is `DRAFT`)
        # 3. Catalogue Entry is `assigned_to` the request user
        # 4. User is in the Catalogue Editor group
        modify_is_permitted = (
            hasattr(obj, "catalogue_entry")
            and isinstance(obj.catalogue_entry, models.catalogue_entries.CatalogueEntry)
            and obj.catalogue_entry.status == models.catalogue_entries.CatalogueEntryStatus.DRAFT
            and obj.catalogue_entry.assigned_to == request.user
            and utils.is_catalogue_editor(request.user)
        )

        # Check permissions and return
        return read_is_permitted or modify_is_permitted
