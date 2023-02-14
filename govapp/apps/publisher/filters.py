"""Kaartdijin Boodja Publisher Django Application Filters."""


# Third-Party
from django_filters import rest_framework as filters

# Local
from govapp.apps.publisher import models


class CDDPPublishChannelFilter(filters.FilterSet):
    """CDDP Publish Channel Filter."""
    class Meta:
        """CDDP Publish Channel Filter Metadata."""
        model = models.publish_channels.CDDPPublishChannel
        fields = ()


class GeoServerPublishChannelFilter(filters.FilterSet):
    """GeoServer Publish Channel Filter."""
    class Meta:
        """GeoServer Publish Channel Filter Metadata."""
        model = models.publish_channels.GeoServerPublishChannel
        fields = ()


class PublishEntryFilter(filters.FilterSet):
    """Publish Entry Filter."""
    updated = filters.IsoDateTimeFromToRangeFilter(field_name="updated_at")
    order_by = filters.OrderingFilter(fields=("id", "name", "status", "updated_at", "assigned_to"))

    class Meta:
        """Publish Entry Filter Metadata."""
        model = models.publish_entries.PublishEntry
        fields = {"id": ["in"], "assigned_to": ["exact"], "status": ["in", "exact"]}


class EmailNotificationFilter(filters.FilterSet):
    """Email Notification Filter."""
    class Meta:
        """Email Notification Filter Metadata."""
        model = models.notifications.EmailNotification
        fields = {"id": ["in"]}


class WorkspaceFilter(filters.FilterSet):
    """Workspace Filter."""
    class Meta:
        """Workspace Filter Metadata."""
        model = models.workspaces.Workspace
        fields = ()
