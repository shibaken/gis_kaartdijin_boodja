"""Kaartdijin Boodja Publisher Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher import models


class PublishEntrySerializer(serializers.ModelSerializer):
    """Publish Entry Model Serializer."""

    class Meta:
        """Publish Entry Model Serializer Metadata."""
        model = models.publish_entries.PublishEntry
        fields = (
            "id",
            "name",
            "description",
            "status",
            "updated_at",
            "published_at",
            "editors",
            "assigned_to",
            "catalogue_entry",
            "cddp_channel",
            "geoserver_channel",
        )
        read_only_fields = (
            "id",
            "status",
            "updated_at",
            "published_at",
            "editors",
            "assigned_to",
            "catalogue_entry",
            "cddp_channel",
            "geoserver_channel",
        )


class PublishEntryCreateSerializer(serializers.ModelSerializer):
    """Publish Entry Model Create Serializer."""
    class Meta:
        """Publish Entry Model Create Serializer Metadata."""
        model = PublishEntrySerializer.Meta.model
        fields = PublishEntrySerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Catalogue Entry
        read_only_fields = (
            "id",
            "status",
            "updated_at",
            "published_at",
            "editors",
            "assigned_to",
            "cddp_channel",
            "geoserver_channel",
        )
