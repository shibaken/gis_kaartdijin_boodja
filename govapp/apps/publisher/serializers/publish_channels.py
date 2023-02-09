"""Kaartdijin Boodja Publisher Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher import models


class CDDPPublishChannelSerializer(serializers.ModelSerializer):
    """CDDP Publish Channel Model Serializer."""

    class Meta:
        """CDDP Publish Channel Model Serializer Metadata."""
        model = models.publish_channels.CDDPPublishChannel
        fields = (
            "id",
            "name",
            "description",
            "format",
            "mode",
            "frequency",
            "path",
            "publish_entry",
        )
        read_only_fields = (
            "id",
            "publish_entry",
        )


class CDDPPublishChannelCreateSerializer(serializers.ModelSerializer):
    """CDDP Publish Channel Model Create Serializer."""
    class Meta:
        """CDDP Publish Channel Model Create Serializer Metadata."""
        model = CDDPPublishChannelSerializer.Meta.model
        fields = CDDPPublishChannelSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Publish Entry


class GeoServerPublishChannelSerializer(serializers.ModelSerializer):
    """GeoServer Publish Channel Model Serializer."""

    class Meta:
        """GeoServer Publish Channel Model Serializer Metadata."""
        model = models.publish_channels.GeoServerPublishChannel
        fields = (
            "id",
            "name",
            "description",
            "mode",
            "frequency",
            "workspace",
            "publish_entry",
        )
        read_only_fields = (
            "id",
            "publish_entry",
        )


class GeoServerPublishChannelCreateSerializer(serializers.ModelSerializer):
    """GeoServer Publish Channel Model Create Serializer."""
    class Meta:
        """GeoServer Publish Channel Model Create Serializer Metadata."""
        model = GeoServerPublishChannelSerializer.Meta.model
        fields = GeoServerPublishChannelSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Publish Entry
