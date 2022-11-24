"""Kaartdijin Boodja Catalogue Django Application Views."""


# Third-Party
from drf_spectacular import utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets

# Local
from . import filters
from . import mixins
from . import models
from . import permissions
from . import serializers

# Typing
from typing import cast


@utils.extend_schema(tags=["Catalogue - Catalogue Entries"])
class CatalogueEntryViewSet(
    mixins.ChoicesMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """Catalogue Entry View Set."""
    queryset = models.catalogue_entries.CatalogueEntry.objects.all()
    serializer_class = serializers.catalogue_entries.CatalogueEntrySerializer
    filterset_class = filters.CatalogueEntryFilter
    permission_classes = [permissions.CatalogueEntryPermissions]

    @utils.extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @decorators.action(detail=True, methods=["POST"])
    def lock(self, request: request.Request, pk: str) -> response.Response:
        """Locks the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Set Catalogue Entry to Locked
        catalogue_entry.status = models.catalogue_entries.CatalogueEntryStatus.LOCKED
        catalogue_entry.save()

        # Return Response
        return response.Response(status=status.HTTP_200_OK)

    @utils.extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @decorators.action(detail=True, methods=["POST"])
    def unlock(self, request: request.Request, pk: str) -> response.Response:
        """Unlocks the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Set Catalogue Entry to Locked
        catalogue_entry.status = models.catalogue_entries.CatalogueEntryStatus.DRAFT
        catalogue_entry.save()

        # Return Response
        return response.Response(status=status.HTTP_200_OK)


@utils.extend_schema(tags=["Catalogue - Custodians"])
class CustodianViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Custodian View Set."""
    queryset = models.custodians.Custodian.objects.all()
    serializer_class = serializers.custodians.CustodianSerializer
    filterset_class = filters.CustodianFilter


@utils.extend_schema(tags=["Catalogue - Layer Attributes"])
class LayerAttributeViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Attribute View Set."""
    queryset = models.layer_attributes.LayerAttribute.objects.all()
    serializer_class = serializers.layer_attributes.LayerAttributeSerializer
    filterset_class = filters.LayerAttributeFilter


@utils.extend_schema(tags=["Catalogue - Layer Metadata"])
class LayerMetadataViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Metadata View Set."""
    queryset = models.layer_metadata.LayerMetadata.objects.all()
    serializer_class = serializers.layer_metadata.LayerMetadataSerializer
    filterset_class = filters.LayerMetadataFilter


@utils.extend_schema(tags=["Catalogue - Layer Submissions"])
class LayerSubmissionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter


@utils.extend_schema(tags=["Catalogue - Layer Subscriptions"])
class LayerSubscriptionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Subscription View Set."""
    queryset = models.layer_subscriptions.LayerSubscription.objects.all()
    serializer_class = serializers.layer_subscriptions.LayerSubscriptionSerializer
    filterset_class = filters.LayerSubscriptionFilter


@utils.extend_schema(tags=["Catalogue - Layer Symbology"])
class LayerSymbologyViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Symbology View Set."""
    queryset = models.layer_symbology.LayerSymbology.objects.all()
    serializer_class = serializers.layer_symbology.LayerSymbologySerializer
    filterset_class = filters.LayerSymbologyFilter


@utils.extend_schema(tags=["Catalogue - Notifications"])
class EmailNotificationViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Email Notification View Set."""
    queryset = models.notifications.EmailNotification.objects.all()
    serializer_class = serializers.notifications.EmailNotificationSerializer
    filterset_class = filters.EmailNotificationFilter


@utils.extend_schema(tags=["Catalogue - Notifications"])
class WebhookNotificationViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Webhook Notification View Set."""
    queryset = models.notifications.WebhookNotification.objects.all()
    serializer_class = serializers.notifications.WebhookNotificationSerializer
    filterset_class = filters.WebhookNotificationFilter
