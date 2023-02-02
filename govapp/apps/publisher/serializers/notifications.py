"""Kaartdijin Boodja Publisher Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher import models


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Email Notification Model Serializer."""
    class Meta:
        """Email Notification Model Serializer Metadata."""
        model = models.notifications.EmailNotification
        fields = ("id", "name", "type", "email", "publish_entry")
        read_only_fields = ("id", "publish_entry")


class EmailNotificationCreateSerializer(serializers.ModelSerializer):
    """Email Notification Model Create Serializer."""
    class Meta:
        """Email Notification Model Create Serializer Metadata."""
        model = EmailNotificationSerializer.Meta.model
        fields = EmailNotificationSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry
