"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from .. import models


class WorkspaceSerializer(serializers.ModelSerializer):
    """Workspace Model Serializer."""
    class Meta:
        """Workspace Model Serializer Metadata."""
        model = models.workspaces.Workspace
        fields = ("id", "name")
