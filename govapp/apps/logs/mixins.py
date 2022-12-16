"""Kaartdijin Boodja Logs Django Application Utility Functions."""


# Third-Party
from django import http
from django import shortcuts
from django.contrib.contenttypes import models as ct_models
from django.db import models as db_models
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import serializers as rf_serializers
from rest_framework import viewsets

# Local
from . import models
from . import serializers


class CommunicationsLogMixin:
    """Provides Communications Log API Endpoints for a Model Viewset."""

    # Serializer
    serializer: rf_serializers.ListSerializer = drf_utils.inline_serializer(  # type: ignore
        name=models.CommunicationsLogEntryType.__name__,
        fields={
            "id": rf_serializers.IntegerField(read_only=True),
            "label": rf_serializers.CharField(),
        },
        many=True,
    )

    @drf_utils.extend_schema(filters=False, responses=serializer)
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/communications/type")
    def communications_logs_type_list(self, request: request.Request, pk: str) -> response.Response:
        """_summary_.

        Args:
            request (request.Request): _description_
            pk (str): _description_

        Returns:
            response.Response: _description_
        """
        # Check Viewset, QuerySet and Model
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101
        assert isinstance(self.queryset, db_models.QuerySet)  # noqa: S101
        assert issubclass(self.queryset.model, db_models.Model)  # noqa: S101

        # Retrieve Field Choices
        choices = models.CommunicationsLogEntryType.choices

        # Construct Results
        results = {str(pk): {"id": pk, "label": label} for (pk, label) in choices}

        # Paginate and Return
        return self.get_paginated_response(
            data=self.paginate_queryset(
                queryset=list(results.values()),
            )
        )

    @drf_utils.extend_schema(filters=False, responses=serializer.child)
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/communications/type/(?P<type_pk>\d+)")
    def communications_logs_type_detail(self, request: request.Request, pk: str, type_pk: str) -> response.Response:
        """_summary_.

        Args:
            request (request.Request): _description_
            pk (str): _description_

        Returns:
            response.Response: _description_
        """
        # Check Viewset, QuerySet and Model
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101
        assert isinstance(self.queryset, db_models.QuerySet)  # noqa: S101
        assert issubclass(self.queryset.model, db_models.Model)  # noqa: S101

        # Retrieve Field Choices
        choices = models.CommunicationsLogEntryType.choices

        # Construct Results
        results = {str(pk): {"id": pk, "label": label} for (pk, label) in choices}

        # Retrieve Type
        if obj := results.get(type_pk):
            # Return Type
            return response.Response(obj)

        # Raise 404
        raise http.Http404

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
        # Check Viewset, QuerySet and Model
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101
        assert isinstance(self.queryset, db_models.QuerySet)  # noqa: S101
        assert issubclass(self.queryset.model, db_models.Model)  # noqa: S101

        # Retrieve Parent Model
        parent = shortcuts.get_object_or_404(
            self.queryset.model,
            id=pk,
        )

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=parent,
        )

        # Retrieve Logs Queryset for Parent Model
        queryset = models.CommunicationsLogEntry.objects.filter(
            content_type=content_type,
            object_id=pk,
        )

        # Get Page
        page = self.paginate_queryset(queryset=queryset)

        # Serialize
        serializer = serializers.CommunicationsLogEntrySerializer(page, many=True)

        # Return Response
        return self.get_paginated_response(data=serializer.data)

    @drf_utils.extend_schema(filters=False, responses=serializers.CommunicationsLogEntrySerializer)
    @decorators.action(detail=True, methods=["GET"], url_path=r"logs/communications/(?P<log_pk>\d+)")
    def communications_logs_detail(self, request: request.Request, pk: str, log_pk: str) -> response.Response:
        """Retrieves the Communications Log Entries for this Model.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the model the logs are associated with.
            log_pk (str): Primary key of the log itself.

        Returns:
            response.Response: Communications log detail response.
        """
        # Check Viewset, QuerySet and Model
        assert isinstance(self, viewsets.GenericViewSet)  # noqa: S101
        assert isinstance(self.queryset, db_models.QuerySet)  # noqa: S101
        assert issubclass(self.queryset.model, db_models.Model)  # noqa: S101

        # Retrieve Parent Model
        parent = shortcuts.get_object_or_404(
            self.queryset.model,
            id=pk,
        )

        # Determine Parent Model Content Type
        content_type = ct_models.ContentType.objects.get_for_model(
            model=parent,
        )

        # Retrieve Logs Queryset
        log = shortcuts.get_object_or_404(
            models.CommunicationsLogEntry,
            content_type=content_type,
            object_id=pk,
            id=log_pk,
        )

        # Serialize
        serializer = serializers.CommunicationsLogEntrySerializer(log)

        # Return
        return response.Response(serializer.data)


class ActionsLogMixin:
    """Provides Actions Log API Endpoints for a Model Viewset."""
    # Gives /logs/actions/
    #       /logs/actions/x/
