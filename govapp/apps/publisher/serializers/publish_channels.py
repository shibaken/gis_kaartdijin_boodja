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
            #"description",
            "published_at",
            "format",
            "mode",
            "frequency",
            "path",
            "publish_entry",
        )
        read_only_fields = (
            "id",        
            "published_at",
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
        read_only_fields = (
            "id",
            "published_at",
        )


class GeoServerPublishChannelSerializer(serializers.ModelSerializer):
    """GeoServer Publish Channel Model Serializer."""
    workspace_name = serializers.ReadOnlyField(source='workspace.name')
    
    class Meta:
        """GeoServer Publish Channel Model Serializer Metadata."""
        model = models.publish_channels.GeoServerPublishChannel
        fields = "__all__"
        # fields = (
        #     "id",
        #     #"name",
        #     #"description",
        #     "published_at",
        #     "mode",
        #     "frequency",
        #     "workspace",
        #     "publish_entry",
        #     "workspace_name"
        # )
        read_only_fields = (
            "id",
            "name",
            "published_at",
            "publish_entry",
            "workspace_name",
            "name",
            "description"
        )
        
    def validate(self, data):
        _validate_bbox(data)
        return data
        


class GeoServerPublishChannelCreateSerializer(serializers.ModelSerializer):
    """GeoServer Publish Channel Model Create Serializer."""
    class Meta:
        """GeoServer Publish Channel Model Create Serializer Metadata."""
        model = GeoServerPublishChannelSerializer.Meta.model
        fields = GeoServerPublishChannelSerializer.Meta.fields
        # No read only fields on this serializer
        # This allows the `create` action to specify a Publish Entry
        read_only_fields = (
            "id",
            "name",
            "published_at",
        )
    
    def validate(self, data):
        _validate_bbox(data)
        return data

def _validate_bbox(data):
    if not data['override_bbox']:
        return
    if _has_null(data['native_crs'], 
                    data['nbb_minx'], data['nbb_maxx'], data['nbb_miny'], data['nbb_maxy'], data['nbb_crs'],
                    data['llb_minx'], data['llb_maxx'], data['llb_miny'], data['llb_maxy'], data['llb_crs']):
        raise serializers.ValidationError("'If override_bbox is True, every related fields must be filled.")
        
def _has_null(*args):
    for arg in args:
        if arg == None:
            return True
    return False
