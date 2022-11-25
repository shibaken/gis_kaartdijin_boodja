"""Kaartdijin Boodja Accounts Django Application Views."""


# Third-Party
from django.contrib import auth
from django.contrib.auth import models
from drf_spectacular import utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import viewsets

# Local
from . import serializers
from . import filters


# Shortcuts
UserModel = auth.get_user_model()
GroupModel = models.Group


@utils.extend_schema(tags=["Accounts - Users"])
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User View Set."""
    queryset = UserModel.objects.all()
    serializer_class = serializers.UserSerializer
    filterset_class = filters.UserFilter

    @utils.extend_schema(request=None, responses=serializers.UserSerializer)
    @decorators.action(detail=False, methods=["GET"])
    def me(self, request: request.Request) -> response.Response:
        """Retrieves the currently logged in user.

        Args:
            request (request.Request): API request.

        Returns:
            response.Response: The currently logged in user if applicable.
        """
        # Retrieve User
        instance = request.user

        # Serialize User
        serializer = self.get_serializer(instance)

        # Return Response
        return response.Response(serializer.data)


@utils.extend_schema(tags=["Accounts - Groups"])
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Group View Set."""
    queryset = GroupModel.objects.all()
    serializer_class = serializers.GroupSerializer
