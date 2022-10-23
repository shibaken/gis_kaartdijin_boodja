"""Kaartdijin Boodja Catalogue Django Application Filters."""


# Third-Party
from django_filters import rest_framework as filters

# Local
from . import models


class CatalogueEntryFilter(filters.FilterSet):
    """Catalogue Entry Filter."""
    updated = filters.IsoDateTimeFromToRangeFilter(field_name="updated_at")
    order_by = filters.OrderingFilter(fields=("id", "name", "status", "updated_at", "custodian", "assigned_to"))

    class Meta:
        """Catalogue Entry Filter Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = ("assigned_to", "custodian", "status", "updated")


class LayerAttributeFilter(filters.FilterSet):
    """Layer Attribute Filter."""
    class Meta:
        """Layer Attribute Filter Metadata."""
        model = models.layer_attributes.LayerAttribute
        fields = ()


class LayerMetadataFilter(filters.FilterSet):
    """Layer Metadata Filter."""
    class Meta:
        """Layer Metadata Filter Metadata.."""
        model = models.layer_metadata.LayerMetadata
        fields = ()


class LayerSubmissionFilter(filters.FilterSet):
    """Layer Submission Filter."""
    submitted = filters.IsoDateTimeFromToRangeFilter(field_name="submitted_at")
    order_by = filters.OrderingFilter(fields=("id", "name", "status", "submitted_at", "catalogue_entry"))

    class Meta:
        """Layer Submission Filter Metadata."""
        model = models.layer_submissions.LayerSubmission
        fields = ("status", "submitted")


class LayerSubscriptionFilter(filters.FilterSet):
    """Layer Subscription Filter."""
    subscribed = filters.IsoDateTimeFromToRangeFilter(field_name="subscribed_at")
    order_by = filters.OrderingFilter(fields=("id", "name", "url", "status", "subscribed_at"))

    class Meta:
        """Layer Subscription Filter Metadata."""
        model = models.layer_subscriptions.LayerSubscription
        fields = ("status", "subscribed")


class LayerSymbologyFilter(filters.FilterSet):
    """Layer Symbology Filter."""
    class Meta:
        """Layer Symbology Filter Metadata."""
        model = models.layer_symbology.LayerSymbology
        fields = ()


class EmailNotificationFilter(filters.FilterSet):
    """Email Notification Filter."""
    class Meta:
        """Email Notification Filter Metadata."""
        model = models.notifications.EmailNotification
        fields = ()


class WebhookNotificationFilter(filters.FilterSet):
    """Webhook Notification Filter."""
    class Meta:
        """Webhook Notification Filter Metadata."""
        model = models.notifications.WebhookNotification
        fields = ()
