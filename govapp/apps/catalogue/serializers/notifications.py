"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Email Notification Model Serializer."""
    
    def validate_email(self, email):
         pk = self.context.get('pk')
         catalogue_entry = models.notifications.EmailNotification.objects.get(id=pk).catalogue_entry
         if models.notifications.EmailNotification.objects.filter(catalogue_entry=catalogue_entry, email=email).exclude(id=pk).exists():
             raise serializers.ValidationError("Email '{}' is already taken.".format(email))
         return email
     
    class Meta:
        """Email Notification Model Serializer Metadata."""
        model = models.notifications.EmailNotification
        fields = ("id", "name", "type", "email", "active", "catalogue_entry")
        read_only_fields = ("id", "catalogue_entry")


class WebhookNotificationSerializer(serializers.ModelSerializer):
    """Webhook Notification Model Serializer."""
    class Meta:
        """Webhook Notification Model Serializer Metadata."""
        model = models.notifications.WebhookNotification
        fields = ("id", "name", "type", "url", "catalogue_entry")
        read_only_fields = ("id", "catalogue_entry")


class EmailNotificationCreateSerializer(serializers.ModelSerializer):
    """Email Notification Model Create Serializer."""
    
    def validate_email(self, email):
        catalogue_entry = self.initial_data.get('catalogue_entry')
        if models.notifications.EmailNotification.objects.filter(catalogue_entry=catalogue_entry, email=email).exists():
            raise serializers.ValidationError("Email '{}' is already taken.".format(email))
        return email
     
    class Meta:
        """Email Notification Model Create Serializer Metadata."""
        model = EmailNotificationSerializer.Meta.model
        fields = EmailNotificationSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry


class WebhookNotificationCreateSerializer(serializers.ModelSerializer):
    """Webhook Notification Model Create Serializer."""
    class Meta:
        """Webhook Notification Model Create Serializer Metadata."""
        model = WebhookNotificationSerializer.Meta.model
        fields = WebhookNotificationSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry
