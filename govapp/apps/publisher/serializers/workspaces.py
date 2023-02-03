"""Kaartdijin Boodja Publisher Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher import models


class WorkspaceSerializer(serializers.ModelSerializer):
    """Workspace Model Serializer."""
    class Meta:
        """Workspace Model Serializer Metadata."""
        model = models.workspaces.Workspace
        fields = ("id", "name")
