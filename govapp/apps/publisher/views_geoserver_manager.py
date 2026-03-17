"""Views for the kb-geoserver-manager API."""

# Standard
import logging
import os

# Third-Party
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Local
from govapp.apps.publisher.models import geoserver_queues
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueueStatus
from govapp.apps.publisher.serializers.geoserver_manager import (
    GEOSERVER_MANAGER_WRITABLE_STATUSES,
    STATUS_INT_TO_STR,
    GeoServerManagerLayerSerializer,
    GeoServerManagerStatusUpdateSerializer,
)

# Logging
log = logging.getLogger(__name__)

# Map status query string to GeoServerQueueStatus integer
STATUS_STR_TO_INT = {v: k for k, v in STATUS_INT_TO_STR.items()}

# Valid status transitions allowed from kb-geoserver-manager
# key: current status → value: set of statuses that kb-geoserver-manager may transition to
ALLOWED_TRANSITIONS: dict[int, set[int]] = {
    GeoServerQueueStatus.READY: {GeoServerQueueStatus.UPLOAD_IN_PROGRESS},
    GeoServerQueueStatus.UPLOAD_IN_PROGRESS: {
        GeoServerQueueStatus.UPLOAD_FAILED,
        GeoServerQueueStatus.READY_TO_PUBLISH,
    },
    GeoServerQueueStatus.READY_TO_PUBLISH: {
        GeoServerQueueStatus.PUBLISHED,
        GeoServerQueueStatus.PUBLISH_FAILED,
    },
    # Retry transitions
    GeoServerQueueStatus.UPLOAD_FAILED: {GeoServerQueueStatus.READY},
    GeoServerQueueStatus.PUBLISH_FAILED: {GeoServerQueueStatus.READY_TO_PUBLISH},
}

CHUNK_SIZE = 8 * 1024  # 8 KB


def _file_chunk_generator(filepath: str):
    """Yields file contents in CHUNK_SIZE byte increments."""
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


class GeoServerManagerViewSet(viewsets.GenericViewSet):
    """API endpoints consumed by kb-geoserver-manager.

    Supported operations:
      GET  /api/geoserver-manager/layers/?status=<status>  — list layers by status
      GET  /api/geoserver-manager/layers/<pk>/download/    — stream file in chunks
      PATCH /api/geoserver-manager/layers/<pk>/            — update layer status
    """

    queryset = geoserver_queues.GeoServerQueue.objects.select_related(
        "publish_entry__catalogue_entry"
    ).prefetch_related(
        "publish_entry__catalogue_entry__layers"
    )
    serializer_class = GeoServerManagerLayerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """List GeoServerQueue items filtered by status query parameter."""
        status_str = request.query_params.get("status")
        if not status_str:
            return Response(
                {"detail": "Query parameter 'status' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_int = STATUS_STR_TO_INT.get(status_str)
        if status_int is None:
            return Response(
                {"detail": f"Unknown status '{status_str}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self.get_queryset().filter(
            status=status_int,
            queue_type=geoserver_queues.GeoServerQueueType.PUBLISH,
        )
        serializer = GeoServerManagerLayerSerializer(qs, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Update the status of a GeoServerQueue item."""
        queue_item = self.get_object()

        serializer = GeoServerManagerStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status_str = serializer.validated_data["status"]
        new_status_int = GEOSERVER_MANAGER_WRITABLE_STATUSES[new_status_str]

        allowed_next = ALLOWED_TRANSITIONS.get(queue_item.status, set())
        if new_status_int not in allowed_next:
            current_label = STATUS_INT_TO_STR.get(queue_item.status, str(queue_item.status))
            return Response(
                {
                    "detail": (
                        f"Cannot transition from '{current_label}' to '{new_status_str}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queue_item.change_status(new_status_int)
        log.info(
            f"GeoServerQueue [{queue_item.id}] status updated to '{new_status_str}' "
            f"by kb-geoserver-manager (user: {request.user})."
        )

        return Response(
            GeoServerManagerLayerSerializer(queue_item).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Stream the GIS file associated with this GeoServerQueue item."""
        queue_item = self.get_object()

        active_layer = queue_item.publish_entry.catalogue_entry.active_layer
        if active_layer is None:
            return Response(
                {"detail": "No active layer file found for this entry."},
                status=status.HTTP_404_NOT_FOUND,
            )

        filepath = active_layer.file
        if not os.path.isfile(filepath):
            log.error(f"File not found on disk: {filepath}")
            return Response(
                {"detail": "File not found on server."},
                status=status.HTTP_404_NOT_FOUND,
            )

        filename = os.path.basename(filepath)
        streaming_response = StreamingHttpResponse(
            _file_chunk_generator(filepath),
            content_type="application/octet-stream",
        )
        streaming_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        streaming_response["Content-Length"] = os.path.getsize(filepath)
        return streaming_response
