"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerAttributeSerializer(serializers.ModelSerializer):
    """Layer Attribute Model Serializer."""

    def validate_order(self, order):
         att_id = self.context.get('pk')
         catalogue_entry = models.layer_attributes.LayerAttribute.objects.get(id=att_id).catalogue_entry
         if models.layer_attributes.LayerAttribute.objects.filter(catalogue_entry=catalogue_entry, order=order).exclude(id=att_id).exists():
             raise serializers.ValidationError("Value '{}' of 'order' is already taken.".format(order))
         return order

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

    def validate_order(self, order):
         catalogue_entry = self.initial_data.get('catalogue_entry')
         if models.layer_attributes.LayerAttribute.objects.filter(catalogue_entry=catalogue_entry, order=order).exists():
             raise serializers.ValidationError("Value '{}' of 'order' is already taken.".format(order))
         return order