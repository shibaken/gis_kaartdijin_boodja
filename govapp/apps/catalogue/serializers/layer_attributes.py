"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from django.db import transaction
from django.db.models import Max, F
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerAttributeSerializer(serializers.ModelSerializer):
    """Layer Attribute Model Serializer."""

    def validate_order(self, order):
        # NOTE: If order validation is needed for updates, handle here
        return order

    class Meta:
        """Layer Attribute Model Serializer Metadata."""
        model = models.layer_attributes.LayerAttribute
        fields = ("id", "name", "type", "order", "catalogue_entry")
        read_only_fields = ("id", "catalogue_entry")


class LayerAttributeCreateSerializer(serializers.ModelSerializer):
    """Layer Attribute Model Create Serializer."""
    # Allow order to be optional (if not provided, it will be added to the end)
    order = serializers.IntegerField(required=False, min_value=1)

    class Meta:
        """Layer Attribute Model Create Serializer Metadata."""
        model = LayerAttributeSerializer.Meta.model
        fields = LayerAttributeSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry

    def create(self, validated_data):
        """Create a LayerAttribute and shift existing attributes order if necessary."""
        catalogue_entry = validated_data.get('catalogue_entry')
        target_order = validated_data.get('order')

        with transaction.atomic():
            # If order is not specified, assign it to the end of the list
            if target_order is None:
                max_order = models.layer_attributes.LayerAttribute.objects.filter(
                    catalogue_entry=catalogue_entry
                ).aggregate(Max('order'))['order__max']
                
                target_order = (max_order or 0) + 1
                validated_data['order'] = target_order
            else:
                # Shift all existing attributes with order >= target_order by +1
                models.layer_attributes.LayerAttribute.objects.filter(
                    catalogue_entry=catalogue_entry,
                    order__gte=target_order
                ).update(order=F('order') + 1)

            # Create the new LayerAttribute
            return super().create(validated_data)