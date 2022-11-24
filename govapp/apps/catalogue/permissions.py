"""Kaartdijin Boodja Catalogue Django Application Administration."""


# Third-Party
from django import conf
from rest_framework import permissions
from rest_framework import request
from rest_framework import views

# Local
from . import models

# Typing
from typing import Any


class CatalogueEntryPermissions(permissions.BasePermission):
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
        catalogue_update_permitted = (
            isinstance(obj, models.catalogue_entries.CatalogueEntry)
            and obj.assigned_to == request.user
            and request.user.groups.filter(id=conf.settings.GROUP_CATALOGUE_EDITOR).exists()  # type: ignore
        )

        # Check permissions and return
        return read_is_permitted or catalogue_update_permitted
