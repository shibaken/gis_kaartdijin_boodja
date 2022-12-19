"""Kaartdijin Boodja Logs Django Application Utility Functions."""


# Third-Party
from django import shortcuts
from django.contrib.contenttypes import models as ct_models
from django.db import models as db_models
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import parsers
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets

# Local
from . import models
from . import serializers


class CommunicationsLogMixin:
    """Provides Communications Log API Endpoints for a Model Viewset."""

    @drf_utils.extend_schema(filters=False, responses=serializers.CommunicationsLogEntrySerializer(many=True))
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/communications")
    def communications_logs_list(self, request: request.Request, pk: str) -> response.Response:
        """Retrieves the Communications Log Entries List for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.

        Returns:
            response.Response: Communications log list response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=model,
        )

        # Retrieve Logs Queryset for Parent Model
        queryset = models.CommunicationsLogEntry.objects.filter(
            content_type=content_type,
            object_id=model.pk,
        )

        # Get Page
        page = self.paginate_queryset(queryset=queryset)

        # Serialize
        serializer = serializers.CommunicationsLogEntrySerializer(
            instance=page,
            context=self.get_serializer_context(),
            many=True,
        )

        # Return Response
        return self.get_paginated_response(data=serializer.data)

    @drf_utils.extend_schema(
        request=serializers.CommunicationsLogEntrySerializer,
        responses=serializers.CommunicationsLogEntrySerializer,
    )
    @communications_logs_list.mapping.post
    def communications_logs_create(self, request: request.Request, pk: str) -> response.Response:
        """Creates a Communications Log Entry for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.

        Returns:
            response.Response: Communications log list response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Create Serializer with Request Data
        serializer = serializers.CommunicationsLogEntrySerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )

        # Validate Request
        serializer.is_valid(raise_exception=True)

        # Save!
        # Update the Instance with the Generic Foreign Key and the User
        serializer.save(content_object=model, user=request.user)

        # Return Response
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @drf_utils.extend_schema(filters=False, responses=serializers.CommunicationsLogEntrySerializer)
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/communications/(?P<log_pk>\d+)")
    def communications_logs_detail(self, request: request.Request, pk: str, log_pk: str) -> response.Response:
        """Retrieves a Communications Log Entry for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.
            log_pk (str): Primary key of the log itself.

        Returns:
            response.Response: Communications log detail response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=model,
        )

        # Retrieve Communications Log
        log = shortcuts.get_object_or_404(
            models.CommunicationsLogEntry,
            content_type=content_type,
            object_id=model.pk,
            id=log_pk,
        )

        # Serialize
        serializer = serializers.CommunicationsLogEntrySerializer(
            instance=log,
            context=self.get_serializer_context(),
        )

        # Return
        return response.Response(serializer.data)

    @drf_utils.extend_schema(
        request=serializers.CommunicationsLogDocumentSerializer,
        responses=serializers.CommunicationsLogDocumentSerializer,
    )
    @decorators.action(
        detail=True,
        methods=["POST"],
        url_path=r"logs/communications/(?P<log_pk>\d+)/file",
        parser_classes=[parsers.MultiPartParser],
    )
    def communications_logs_add_file(self, request: request.Request, pk: str, log_pk: str) -> response.Response:
        """Adds a File to a Communications Log Entry for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.
            log_pk (str): Primary key of the log itself.

        Returns:
            response.Response: Communications log document response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=model,
        )

        # Retrieve Communications Log
        log = shortcuts.get_object_or_404(
            models.CommunicationsLogEntry,
            content_type=content_type,
            object_id=model.pk,
            id=log_pk,
        )

        # Check Permissions
        # To attach a file to a Communications Log, the user must have created
        # the Communications Log in the first place
        if log.user != request.user:
            # Raise 403 Forbidden
            raise exceptions.PermissionDenied

        # Create Serializer with Request Data
        serializer = serializers.CommunicationsLogDocumentSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )

        # Validate Request
        serializer.is_valid(raise_exception=True)

        # Save!
        # Update the Instance with the Entry and the User
        serializer.save(entry=log, user=request.user)

        # Return Response
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class ActionsLogMixin:
    """Provides Actions Log API Endpoints for a Model Viewset."""

    @drf_utils.extend_schema(filters=False, responses=serializers.ActionsLogEntrySerializer(many=True))
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/actions")
    def actions_logs_list(self, request: request.Request, pk: str) -> response.Response:
        """Retrieves the Actions Log Entries List for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.

        Returns:
            response.Response: Actions log list response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=model,
        )

        # Retrieve Logs Queryset for Parent Model
        queryset = models.ActionsLogEntry.objects.filter(
            content_type=content_type,
            object_id=model.pk,
        )

        # Get Page
        page = self.paginate_queryset(queryset=queryset)

        # Serialize
        serializer = serializers.ActionsLogEntrySerializer(
            instance=page,
            context=self.get_serializer_context(),
            many=True,
        )

        # Return Response
        return self.get_paginated_response(data=serializer.data)

    @drf_utils.extend_schema(filters=False, responses=serializers.ActionsLogEntrySerializer)
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/actions/(?P<log_pk>\d+)")
    def actions_logs_detail(self, request: request.Request, pk: str, log_pk: str) -> response.Response:
        """Retrieves an Actions Log Entry for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.
            log_pk (str): Primary key of the log itself.

        Returns:
            response.Response: Actions log detail response.
        """
        # Check Viewset
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101

        # Retrieve Object Model
        model: db_models.Model = self.get_object()

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=model,
        )

        # Retrieve Actions Log
        log = shortcuts.get_object_or_404(
            models.ActionsLogEntry,
            content_type=content_type,
            object_id=model.pk,
            id=log_pk,
        )

        # Serialize
        serializer = serializers.ActionsLogEntrySerializer(
            instance=log,
            context=self.get_serializer_context(),
        )

        # Return
        return response.Response(serializer.data)
