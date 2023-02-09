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
        fields = ("id", "name", "url", "frequency", "status", "subscribed_at", "catalogue_entry")
