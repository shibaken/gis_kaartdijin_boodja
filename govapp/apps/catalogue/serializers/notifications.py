"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from .. import models


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Email Notification Model Serializer."""
    class Meta:
        """Email Notification Model Serializer Metadata."""
        model = models.notifications.EmailNotification
        fields = ("id", "name", "type", "email", "catalogue_entry")


class WebhookNotificationSerializer(serializers.ModelSerializer):
    """Webhook Notification Model Serializer."""
    class Meta:
        """Webhook Notification Model Serializer Metadata."""
        model = models.notifications.WebhookNotification
        fields = ("id", "name", "type", "url", "catalogue_entry")
