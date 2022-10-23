"""Kaartdijin Boodja Catalogue Django Application Views."""


# Third-Party
from rest_framework import viewsets

# Local
from . import filters
from . import mixins
from . import models
from . import serializers


class CatalogueEntryViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Catalogue Entry View Set."""
    queryset = models.catalogue_entries.CatalogueEntry.objects.all()
    serializer_class = serializers.catalogue_entries.CatalogueEntrySerializer
    filterset_class = filters.CatalogueEntryFilter


class LayerAttributeViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Attribute View Set."""
    queryset = models.layer_attributes.LayerAttribute.objects.all()
    serializer_class = serializers.layer_attributes.LayerAttributeSerializer
    filterset_class = filters.LayerAttributeFilter


class LayerMetadataViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Metadata View Set."""
    queryset = models.layer_metadata.LayerMetadata.objects.all()
    serializer_class = serializers.layer_metadata.LayerMetadataSerializer
    filterset_class = filters.LayerMetadataFilter


class LayerSubmissionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter


class LayerSubscriptionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Subscription View Set."""
    queryset = models.layer_subscriptions.LayerSubscription.objects.all()
    serializer_class = serializers.layer_subscriptions.LayerSubscriptionSerializer
    filterset_class = filters.LayerSubscriptionFilter


class LayerSymbologyViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Symbology View Set."""
    queryset = models.layer_symbology.LayerSymbology.objects.all()
    serializer_class = serializers.layer_symbology.LayerSymbologySerializer
    filterset_class = filters.LayerSymbologyFilter


class EmailNotificationViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Email Notification View Set."""
    queryset = models.notifications.EmailNotification.objects.all()
    serializer_class = serializers.notifications.EmailNotificationSerializer
    filterset_class = filters.EmailNotificationFilter


class WebhookNotificationViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Webhook Notification View Set."""
    queryset = models.notifications.WebhookNotification.objects.all()
    serializer_class = serializers.notifications.WebhookNotificationSerializer
    filterset_class = filters.WebhookNotificationFilter
