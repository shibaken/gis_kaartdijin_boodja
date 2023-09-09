"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class CatalogueEntrySerializer(serializers.ModelSerializer):
    """Catalogue Entry Model Serializer."""
    active_layer = serializers.PrimaryKeyRelatedField(read_only=True)  # type: ignore[var-annotated]
    custodian_name = serializers.ReadOnlyField(source='custodian.name',)
    assigned_to_first_name = serializers.ReadOnlyField(source='assigned_to.first_name',)
    assigned_to_last_name = serializers.ReadOnlyField(source='assigned_to.last_name',)
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email',)

    class Meta:
        """Catalogue Entry Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = (
            "id",
            "name",
            "description",
            "status",
            "created_at",
            "updated_at",
            # "editors",
            "custodian",
            "assigned_to",
            # "subscription",
            "active_layer",
            "type",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
            "publish_entry",
            "custodian_name",
            "assigned_to_first_name",
            "assigned_to_last_name",
            "assigned_to_email",
            
        )
        read_only_fields = (
            "id",
            #"name",
            "status",
            "created_at",
            "updated_at",
            # "editors",
            "assigned_to",
            # "subscription",
            "active_layer",
            "type",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
            "publish_entry",
        )

class CatalogueEntryCreateSubscriptionMappingSerializer(serializers.ModelSerializer):
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = ("name", "description", "mapping_name")
    
    def validate(self, data):
        if 'description' not in data or not data['description']:
            raise serializers.ValidationError("'description' field is required.")
        return data

class CatalogueEntryUpdateSubscriptionMappingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    mapping_name = serializers.CharField(required=False)
    
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = CatalogueEntryCreateSubscriptionMappingSerializer.Meta.model
        fields = CatalogueEntryCreateSubscriptionMappingSerializer.Meta.fields
        
class CatalogueEntryGetSubscriptionMappingSerializer(serializers.ModelSerializer):
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = CatalogueEntryCreateSubscriptionMappingSerializer.Meta.model
        fields = CatalogueEntryCreateSubscriptionMappingSerializer.Meta.fields
        read_only_fields = CatalogueEntryCreateSubscriptionMappingSerializer.Meta.fields