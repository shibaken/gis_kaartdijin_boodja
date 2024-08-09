"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
import pytz
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
    updated_at = serializers.SerializerMethodField()
    permission_type_str = serializers.SerializerMethodField()

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
            "custodian",
            "assigned_to",
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
            "permission_type",
            "permission_type_str",
            "force_run_postgres_scanner",
        )
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "updated_at",
            "assigned_to",
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

    def get_permission_type_str(self, obj):
        return obj.get_permission_type_display()

    def get_updated_at(self, obj):
        """Convert updated_at to the desired format."""
        if obj.updated_at:
            # Convert to local time
            local_time = obj.updated_at.astimezone(pytz.timezone('Australia/Perth'))
            # Return formatted string
            # return local_time.strftime('%d %b %Y %I:%M %p')
            return local_time.strftime('%d-%m-%Y %H:%M:%S')
        return None


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
        

class CatalogueEntryCreateSubscriptionQuerySerializer(serializers.ModelSerializer):
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = ("name", "description", "sql_query")
    
    def validate(self, data):
        if 'description' not in data or not data['description']:
            raise serializers.ValidationError("'description' field is required.")
        if 'sql_query' not in data or not data['sql_query']:
            raise serializers.ValidationError("'sql_query' field is required.")
        return data

class CatalogueEntryUpdateSubscriptionQuerySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    sql_query = serializers.CharField(required=False)
    
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = CatalogueEntryCreateSubscriptionQuerySerializer.Meta.model
        fields = CatalogueEntryCreateSubscriptionQuerySerializer.Meta.fields
        
class CatalogueEntryGetSubscriptionQuerySerializer(serializers.ModelSerializer):
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = CatalogueEntryCreateSubscriptionQuerySerializer.Meta.model
        fields = CatalogueEntryCreateSubscriptionQuerySerializer.Meta.fields
        read_only_fields = CatalogueEntryCreateSubscriptionQuerySerializer.Meta.fields