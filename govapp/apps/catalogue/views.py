"""Kaartdijin Boodja Catalogue Django Application Views."""


# Third-Party
from django import shortcuts
from django.contrib import auth
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from reversion_rest_framework import mixins as reversion_mixins

# Local
from . import filters
from . import mixins
from . import models
from . import permissions
from . import reversion  # noqa: F401
from . import serializers
from ..accounts import permissions as accounts_permissions
from ..logs import mixins as logs_mixins

# Typing
from typing import cast


# Shortcuts
UserModel = auth.get_user_model()


@drf_utils.extend_schema(tags=["Catalogue - Catalogue Entries"])
class CatalogueEntryViewSet(
    mixins.ChoicesMixin,
    logs_mixins.CommunicationsLogMixin,
    logs_mixins.ActionsLogMixin,
    reversion_mixins.HistoryMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Catalogue Entry View Set."""
    queryset = models.catalogue_entries.CatalogueEntry.objects.all()
    serializer_class = serializers.catalogue_entries.CatalogueEntrySerializer
    filterset_class = filters.CatalogueEntryFilter
    permission_classes = [permissions.IsCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
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

        # Lock
        catalogue_entry.lock()

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
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

        # Unlock
        catalogue_entry.unlock()

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def decline(self, request: request.Request, pk: str) -> response.Response:
        """Declines the Catalogue Entry.

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

        # Decline
        catalogue_entry.decline()

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path=r"assign/(?P<user_pk>\d+)")
    def assign(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Assigns the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.
            user_pk (str): Primary key of the User to assign to.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Retrieve User
        user = shortcuts.get_object_or_404(UserModel, id=user_pk)

        # Assign!
        catalogue_entry.assign(user)

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unassign(self, request: request.Request, pk: str) -> response.Response:
        """Unassigns the Catalogue Entry.

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

        # Unassign!
        catalogue_entry.unassign()

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@drf_utils.extend_schema(tags=["Catalogue - Custodians"])
class CustodianViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Custodian View Set."""
    queryset = models.custodians.Custodian.objects.all()
    serializer_class = serializers.custodians.CustodianSerializer
    filterset_class = filters.CustodianFilter


@drf_utils.extend_schema(tags=["Catalogue - Layer Attributes"])
class LayerAttributeViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Attribute View Set."""
    queryset = models.layer_attributes.LayerAttribute.objects.all()
    serializer_class = serializers.layer_attributes.LayerAttributeSerializer
    serializer_classes = {"create": serializers.layer_attributes.LayerAttributeCreateSerializer}
    filterset_class = filters.LayerAttributeFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Layer Metadata"])
class LayerMetadataViewSet(
    mixins.ChoicesMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Metadata View Set."""
    queryset = models.layer_metadata.LayerMetadata.objects.all()
    serializer_class = serializers.layer_metadata.LayerMetadataSerializer
    filterset_class = filters.LayerMetadataFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Layer Submissions"])
class LayerSubmissionViewSet(
    mixins.ChoicesMixin,
    logs_mixins.CommunicationsLogMixin,
    logs_mixins.ActionsLogMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter


@drf_utils.extend_schema(tags=["Catalogue - Layer Subscriptions"])
class LayerSubscriptionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Subscription View Set."""
    queryset = models.layer_subscriptions.LayerSubscription.objects.all()
    serializer_class = serializers.layer_subscriptions.LayerSubscriptionSerializer
    filterset_class = filters.LayerSubscriptionFilter


@drf_utils.extend_schema(tags=["Catalogue - Layer Symbology"])
class LayerSymbologyViewSet(
    mixins.ChoicesMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Symbology View Set."""
    queryset = models.layer_symbology.LayerSymbology.objects.all()
    serializer_class = serializers.layer_symbology.LayerSymbologySerializer
    filterset_class = filters.LayerSymbologyFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Notifications (Email)"])
class EmailNotificationViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Email Notification View Set."""
    queryset = models.notifications.EmailNotification.objects.all()
    serializer_class = serializers.notifications.EmailNotificationSerializer
    serializer_classes = {"create": serializers.notifications.EmailNotificationCreateSerializer}
    filterset_class = filters.EmailNotificationFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Notifications (Webhook)"])
class WebhookNotificationViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Webhook Notification View Set."""
    queryset = models.notifications.WebhookNotification.objects.all()
    serializer_class = serializers.notifications.WebhookNotificationSerializer
    serializer_classes = {"create": serializers.notifications.WebhookNotificationCreateSerializer}
    filterset_class = filters.WebhookNotificationFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
