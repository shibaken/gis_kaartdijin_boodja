"""Serializers for the kb-geoserver-manager API."""

# Standard
import os

# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher.models import geoserver_queues
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueueStatus

# Valid status strings accepted from kb-geoserver-manager
GEOSERVER_MANAGER_WRITABLE_STATUSES = {
    "upload_in_progress": GeoServerQueueStatus.UPLOAD_IN_PROGRESS,
    "upload_failed": GeoServerQueueStatus.UPLOAD_FAILED,
    "ready_to_publish": GeoServerQueueStatus.READY_TO_PUBLISH,
    "published": GeoServerQueueStatus.PUBLISHED,
    "publish_failed": GeoServerQueueStatus.PUBLISH_FAILED,
}

# Map integer status values to string labels for outbound responses
STATUS_INT_TO_STR = {
    GeoServerQueueStatus.READY: "ready",
    GeoServerQueueStatus.ON_PUBLISHING: "on_publishing",
    GeoServerQueueStatus.PUBLISHED: "published",
    GeoServerQueueStatus.FAILED: "failed",
    GeoServerQueueStatus.UPLOAD_IN_PROGRESS: "upload_in_progress",
    GeoServerQueueStatus.UPLOAD_FAILED: "upload_failed",
    GeoServerQueueStatus.READY_TO_PUBLISH: "ready_to_publish",
    GeoServerQueueStatus.PUBLISH_FAILED: "publish_failed",
}


class GeoServerManagerLayerSerializer(serializers.ModelSerializer):
    """Read serializer for GeoServerQueue items exposed to kb-geoserver-manager."""

    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = geoserver_queues.GeoServerQueue
        fields = ("id", "name", "status", "file_name")

    def get_name(self, obj: geoserver_queues.GeoServerQueue) -> str:
        return obj.publish_entry.catalogue_entry.name

    def get_status(self, obj: geoserver_queues.GeoServerQueue) -> str:
        return STATUS_INT_TO_STR.get(obj.status, str(obj.status))

    def get_file_name(self, obj: geoserver_queues.GeoServerQueue) -> str:
        active_layer = obj.publish_entry.catalogue_entry.active_layer
        if active_layer is None:
            return ""
        return os.path.basename(active_layer.file)


class GeoServerManagerStatusUpdateSerializer(serializers.Serializer):
    """Write serializer for status updates from kb-geoserver-manager."""

    status = serializers.ChoiceField(choices=list(GEOSERVER_MANAGER_WRITABLE_STATUSES.keys()))
