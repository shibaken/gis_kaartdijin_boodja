"""Kaartdijin Boodja Accounts Django Application Serializers."""


# Third-Party
from django.contrib import auth
from django.contrib.auth import models as auth_models
from rest_framework import serializers


# Shortcuts
UserModel = auth.get_user_model()  # TODO -> Does this work with SSO?
GroupModel = auth_models.Group


class UserSerializer(serializers.ModelSerializer):
    """User Model Serializer."""
    class Meta:
        """User Model Serializer Metadata."""
        model = UserModel
        fields = ("id", "username", "groups")


class GroupSerializer(serializers.ModelSerializer):
    """Group Model Serializer."""
    class Meta:
        """Group Model Serializer Metadata."""
        model = GroupModel
        fields = ("name", "permissions")
