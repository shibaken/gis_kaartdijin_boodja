"""Kaartdijin Boodja Catalogue Django Application Views."""


# Third-Party
from django import shortcuts
from django.contrib import auth
from django.db import connection
from django.http import HttpResponse
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from datetime import timedelta
import json
import os

# Local
from govapp.common import mixins
from govapp.apps.accounts import permissions as accounts_permissions
from govapp.apps.catalogue import filters
from govapp.apps.catalogue import models
from govapp.apps.catalogue import permissions
from govapp.apps.catalogue import serializers
from govapp.apps.catalogue.models import layer_submissions as catalogue_layer_submissions_models
from govapp.apps.logs import mixins as logs_mixins
from govapp.apps.logs import utils as logs_utils


# Typing
from typing import Callable, cast
from typing import Any


# Shortcuts
UserModel = auth.get_user_model()


@drf_utils.extend_schema(tags=["Catalogue - Catalogue Entries"])
class CatalogueEntryViewSet(
    mixins.ChoicesMixin,
    mixins.HistoryMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Catalogue Entry View Set."""
    queryset = models.catalogue_entries.CatalogueEntry.objects.all()
    serializer_class = serializers.catalogue_entries.CatalogueEntrySerializer
    filterset_class = filters.CatalogueEntryFilter
    search_fields = ["name", "description", "assigned_to__username", "assigned_to__email", "custodian__name"]    
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
        success = catalogue_entry.lock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was locked"
            )

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
        success = catalogue_entry.unlock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was unlocked"
            )

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
        success = catalogue_entry.decline()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was declined"
            )

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
        success = catalogue_entry.assign(user)

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action=f"Catalogue entry was assigned to {user} (id: {user.pk})"
            )

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
        success = catalogue_entry.unassign()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was unassigned"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @decorators.action(detail=True, methods=["GET"], permission_classes=[accounts_permissions.IsAuthenticated])
    def layer(self, request: request.Request, pk: str):
        """ Api to provide geojson file

        Args:
            request (request.Request): request object passed by Django framework
            pk (str): uri parameter represents id of layer submission(catalogue id?)

        Returns:
            response.Response: HTTP response with geojson data file
        """
        layer_submission = catalogue_layer_submissions_models.LayerSubmission.objects.filter(catalogue_entry=pk, is_active=True).first()
        map_data = None
        try:
            with open(layer_submission.geojson) as file:
                map_data = file.read()
                map_data = json.loads(map_data)
        except Exception as e:
            return response.Response({"error": 'an exception occured during load a target file.'}, 
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return response.Response(map_data, content_type='application/json', status=status.HTTP_200_OK)
    
    @drf_utils.extend_schema(parameters=[drf_utils.OpenApiParameter("days_ago", type=int, required=True)])
    @decorators.action(detail=False, methods=['GET'])
    def recent(self, request: request.Request):
        """ Api to provide sumary of recent catalogue entries from n hours ago

        Args:
            request (request.Request): request object passed by Django framework - must include integer value of days_ago
            pk (str): uri parameter represents id of layer submission(catalogue id)

        Returns:
            response.Response: HTTP response with a list of summary of recent catalogue entries
        """
        
        days_ago = self.request.query_params.get("days_ago")
        
        # validate days_ago
        if days_ago is None or len(days_ago.strip()) == 0:
            return response.Response({"error": 'Field days_ago is required.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not days_ago.isdigit() or int(days_ago) <= 0:
            return response.Response({"error": 'Field house_ago must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # select query using inner join and filter
        start_date = self.get_db_now() - timedelta(days=int(days_ago))
        filtered = models.layer_submissions.LayerSubmission.objects.select_related('catalogue_entry').filter(catalogue_entry__updated_at__gte=start_date, is_active=True)
        selected = filtered.values('catalogue_entry__id', 'catalogue_entry__name', 'catalogue_entry__created_at', 'catalogue_entry__updated_at', 'id')
        
        # build a response data
        response_data = [{
                'id': entry['catalogue_entry__id'],
                'name': entry['catalogue_entry__name'],
                'created_at': entry['catalogue_entry__created_at'],
                'updated_at': entry['catalogue_entry__updated_at'],
                'active_layer': entry['id']
            } for entry in list(selected)]
        return response.Response(response_data, content_type='application/json', status=status.HTTP_200_OK)
    
    def get_db_now(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW()")
            result = cursor.fetchone()
            current_time = result[0]
        return current_time

@drf_utils.extend_schema(tags=["Catalogue - Custodians"])
class CustodianViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Custodian View Set."""
    queryset = models.custodians.Custodian.objects.all()
    serializer_class = serializers.custodians.CustodianSerializer
    filterset_class = filters.CustodianFilter
    search_fields = ["name", "contact_name", "contact_email", "contact_phone"]


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
    search_fields = ["name", "type", "catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    # to pass the pk to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if context['request'].method == 'PUT':
            context['pk'] = self.kwargs['pk']
        return context


@drf_utils.extend_schema(tags=["Catalogue - Layer Attribute Types"])
class LayerAttributeTypeViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):      
    """Layer Attribute Type View Set."""
    queryset = models.layer_attribute_types.LayerAttributeType.objects.all()
    serializer_class = serializers.layer_attribute_types.LayerAttributeTypeSerializer
    filter_backends = []
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    pagination_class = None

    
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
    search_fields = ["catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Layer Submissions"])
class LayerSubmissionViewSet(
    mixins.ChoicesMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter
    search_fields = ["description", "catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    @decorators.action(detail=True, methods=["GET"], url_path="file", permission_classes=[accounts_permissions.IsAuthenticated])
    def download_file(self, request: request.Request, pk: str):
        file_path = self.queryset.get(id=pk).file

        if file_path == None or os.path.exists(file_path) == False:
            return response.Response({"message":"The target file does not exist."}, 
                                     content_type='application/json', 
                                     status=status.HTTP_404_NOT_FOUND)
            
        with open(file_path, 'rb') as fh:
            res = HttpResponse(fh.read(), 
                                content_type='application/octet-stream', 
                                status=status.HTTP_200_OK)
            res['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            res['Filename'] = os.path.basename(file_path)
            return res
        

@drf_utils.extend_schema(tags=["Catalogue - Layer Subscriptions"])
class LayerSubscriptionViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Layer Subscription View Set."""
    queryset = models.layer_subscriptions.LayerSubscription.objects.all()
    serializer_class = serializers.layer_subscriptions.LayerSubscriptionSerializer
    filterset_class = filters.LayerSubscriptionFilter
    search_fields = ["catalogue_entry__name"]


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
    search_fields = ["catalogue_entry__name"]
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
    search_fields = ["name", "email"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    
    # to pass the pk to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if context['request'].method == 'PUT':
            context['pk'] = self.kwargs['pk']
        return context
    

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
    search_fields = ["name", "url"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
