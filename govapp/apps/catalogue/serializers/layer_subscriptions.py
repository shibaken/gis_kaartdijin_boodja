"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerSubscriptionSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.layer_subscriptions.LayerSubscription
        fields = ("id", "name", "description", "type", "enabled", 
                  "url", "username", "connection_timeout", "max_connections", 
                  "read_timeout", "created_at", "updated_at", "workspace")
        read_only_fields = fields
        
class LayerSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = LayerSubscriptionSerializer.Meta.model
        fields = ("name", "description", "type", "enabled", 
                  "url", "username", "connection_timeout", "max_connections", 
                  "read_timeout", "created_at", "updated_at", "workspace")
