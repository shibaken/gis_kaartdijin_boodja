"""Kaartdijin Boodja Accounts Django Application Views."""


# Third-Party
from django.contrib import auth
from django.contrib.auth import models
from rest_framework import viewsets

# Local
from . import serializers


# Shortcuts
UserModel = auth.get_user_model()  # TODO -> Does this work with SSO?
GroupModel = models.Group


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User View Set."""
    queryset = UserModel.objects.all()
    serializer_class = serializers.UserSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Group View Set."""
    queryset = GroupModel.objects.all()
    serializer_class = serializers.GroupSerializer
