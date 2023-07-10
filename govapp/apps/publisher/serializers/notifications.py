"""Kaartdijin Boodja Publisher Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher import models


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Email Notification Model Serializer."""
    
    def validate_email(self, email):
         pk = self.context.get('pk')
         publish_entry = models.notifications.EmailNotification.objects.get(id=pk).publish_entry
         if models.notifications.EmailNotification.objects.filter(publish_entry=publish_entry, email=email).exclude(id=pk).exists():
             raise serializers.ValidationError("Email '{}' is already taken.".format(email))
         return email
     
    class Meta:
        """Email Notification Model Serializer Metadata."""
        model = models.notifications.EmailNotification
        fields = ("id", "name", "type", "email", "active", "publish_entry")
        read_only_fields = ("id", "publish_entry")


class EmailNotificationCreateSerializer(serializers.ModelSerializer):
    """Email Notification Model Create Serializer."""
    
    def validate_email(self, email):
        publish_entry = self.initial_data.get('publish_entry')
        if models.notifications.EmailNotification.objects.filter(publish_entry=publish_entry, email=email).exists():
            raise serializers.ValidationError("Email '{}' is already taken.".format(email))
        return email
    
    
    class Meta:
        """Email Notification Model Create Serializer Metadata."""
        model = EmailNotificationSerializer.Meta.model
        fields = EmailNotificationSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry
