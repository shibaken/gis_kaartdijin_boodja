"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerAttributeSerializer(serializers.ModelSerializer):
    """Layer Attribute Model Serializer."""
    class Meta:
        """Layer Attribute Model Serializer Metadata."""
        model = models.layer_attributes.LayerAttribute
        fields = ("id", "name", "type", "order", "catalogue_entry")
        read_only_fields = ("id", "catalogue_entry")


class LayerAttributeCreateSerializer(serializers.ModelSerializer):
    """Layer Attribute Model Create Serializer."""
    class Meta:
        """Layer Attribute Model Create Serializer Metadata."""
        model = LayerAttributeSerializer.Meta.model
        fields = LayerAttributeSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry
