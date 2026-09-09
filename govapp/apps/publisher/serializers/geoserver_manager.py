"""Serializers for the kb_geoserver_manager API."""

# Standard
import pathlib

# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueue, GeoServerQueueStatus


class GeoServerManagerQueueSerializer(serializers.ModelSerializer):
    """Serializer exposing GeoServerQueue fields needed by kb_geoserver_manager."""

    # Human-readable name of the publish entry
    name = serializers.CharField(source="publish_entry.name", read_only=True)
    # Basename of the converted file — this is the filename the download endpoint will serve
    file_name = serializers.SerializerMethodField()
    # Workspace name from the first active GeoServerPublishChannel
    workspace = serializers.SerializerMethodField()
    # Distinct workspace names across all channels, used to locate directories to delete
    workspaces = serializers.SerializerMethodField()

    class Meta:
        model = GeoServerQueue
        fields = ["id", "name", "status", "file_name", "workspace", "workspaces"]
        read_only_fields = ["id", "name", "file_name", "workspace", "workspaces"]

    def get_file_name(self, obj: GeoServerQueue) -> str | None:
        if obj.converted_file_path:
            return pathlib.Path(obj.converted_file_path).name
        return None

    def get_workspace(self, obj: GeoServerQueue) -> str | None:
        channel = obj.publish_entry.geoserver_channels.filter(active=True).select_related("workspace").first()
        if channel and channel.workspace:
            return channel.workspace.name
        # Fall back to any channel if no active one has a workspace
        channel = obj.publish_entry.geoserver_channels.select_related("workspace").first()
        if channel and channel.workspace:
            return channel.workspace.name
        return None

    def get_workspaces(self, obj: GeoServerQueue) -> list[str]:
        """Distinct workspace names across every channel of this publish entry.

        Used by kb_geoserver_manager to resolve directories to delete for
        AWAITING_FILE_DELETION items. Harmless (but unused) for other statuses.
        """
        names = (
            obj.publish_entry.geoserver_channels
            .exclude(workspace__isnull=True)
            .values_list("workspace__name", flat=True)
            .distinct()
        )
        return list(names)


class GeoServerManagerStatusUpdateSerializer(serializers.Serializer):
    """Validates the status PATCH payload sent by kb_geoserver_manager.

    Only the three transitions that kb_geoserver_manager is authorised to make are
    accepted; all other values are rejected.
    """

    ALLOWED_STATUSES = {
        GeoServerQueueStatus.UPLOAD_IN_PROGRESS,
        GeoServerQueueStatus.UPLOAD_FAILED,
        GeoServerQueueStatus.READY_TO_PUBLISH,
        GeoServerQueueStatus.PUBLISHED,
        GeoServerQueueStatus.PUBLISH_FAILED,
    }

    status = serializers.IntegerField()

    def validate_status(self, value: int) -> int:
        if value not in self.ALLOWED_STATUSES:
            allowed_labels = {
                GeoServerQueueStatus.UPLOAD_IN_PROGRESS: "upload_in_progress",
                GeoServerQueueStatus.UPLOAD_FAILED: "upload_failed",
                GeoServerQueueStatus.READY_TO_PUBLISH: "ready_to_publish",
                GeoServerQueueStatus.PUBLISHED: "published",
                GeoServerQueueStatus.PUBLISH_FAILED: "publish_failed",
            }
            raise serializers.ValidationError(
                f"Invalid status '{value}'. kb_geoserver_manager may only set: "
                + ", ".join(f"{v} ({k})" for k, v in allowed_labels.items())
            )
        return value
