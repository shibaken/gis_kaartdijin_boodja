"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from .. import models


class LayerMetadataSerializer(serializers.ModelSerializer):
    """Layer Metadata Model Serializer."""
    class Meta:
        """Layer Metadata Model Serializer Metadata."""
        model = models.layer_metadata.LayerMetadata
        fields = ("id", "name", "created_at", "layer")
