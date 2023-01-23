"""Kaartdijin Boodja Accounts Django Application Permissions."""


# Third-Party
from rest_framework import permissions
from rest_framework import request
from rest_framework import viewsets

# Local
from govapp.apps.accounts import utils

# Typing
from typing import Any


class IsInAdministratorsGroup(permissions.BasePermission):
    """Permissions for the a user in the Administrators group."""

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
        # Return
        return utils.is_administrator(request.user)

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
        # Return
        return utils.is_administrator(request.user)
