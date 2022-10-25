"""Kaartdijin Boodja Catalogue Django Application Custom Actions."""


# Third-Party
from django import http
from django.db import models
from django.db.models import options
from drf_spectacular import utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import serializers
from rest_framework import viewsets


class ChoicesMixin:
    """Retrieve and list the choices associated with a queryset model."""

    def __init_subclass__(cls) -> None:
        """Hooks into a subclass ViewSet to provide endpoints for choices."""
        # Check Viewset, QuerySet, Model and Model Meta Options
        assert issubclass(cls, viewsets.GenericViewSet)  # noqa: S101
        assert isinstance(cls.queryset, models.QuerySet)  # noqa: S101
        assert issubclass(cls.queryset.model, models.Model)  # noqa: S101
        assert isinstance(cls.queryset.model._meta, options.Options)  # noqa: S101

        # Loop through Fields in the QuerySet Model
        for field in cls.queryset.model._meta.get_fields():
            # Check for Field Choices
            if isinstance(field, models.Field) and field.choices is not None:
                # Add Retrieve and List Actions
                add_actions(cls, cls.queryset.model, field)


def add_actions(
    viewset: type[viewsets.GenericViewSet],
    model: type[models.Model],
    field: models.Field,
) -> None:
    """Adds a choice retrieval and listing actions to the viewset.

    Args:
        viewset (type[viewsets.GenericViewSet]): Viewset to add actions to.
        model (type[models.Model]): Model for the viewset.
        field (models.Field): Field with choices to add the actions for.
    """
    # Retrieve Field Choices
    choices = field.get_choices(include_blank=False)

    # Construct Results
    results = {str(pk): {"id": pk, "label": label} for (pk, label) in choices}

    # Construct Names
    model_name = f"{model.__name__}{field.name.title()}"
    model_description = f"{model_name} Model Serializer."
    name_retrieve = f"{field.name}_retrieve"
    name_list = f"{field.name}_list"
    url_retrieve = fr"{field.name}/(?P<pk>[^/.]+)"

    # Create Mock Serializer for Schema
    serializer: serializers.ListSerializer = utils.inline_serializer(  # type: ignore
        name=model_name,
        fields={
            "id": serializers.IntegerField(read_only=True),
            "label": serializers.CharField(),
        },
        many=True,
    )

    # Set Serializer Docstring
    # This gives the model schema a description
    serializer.child.__class__.__doc__ = model_description

    # Construct Dynamic Retrieve Action Method
    def action_retrieve(self: viewsets.GenericViewSet, request: request.Request, pk: str) -> response.Response:
        if obj := results.get(pk):
            return response.Response(obj)
        raise http.Http404

    # Construct Dynamic List Action Method
    def action_list(self: viewsets.GenericViewSet, request: request.Request) -> response.Response:
        return self.get_paginated_response(
            data=self.paginate_queryset(
                queryset=list(results.values()),
            )
        )

    # Rename Actions
    action_retrieve.__name__ = name_retrieve
    action_list.__name__ = name_list

    # Apply Action Decorators
    # This must be done after the actions are renamed
    action_retrieve = decorators.action(detail=False, url_name=name_retrieve, url_path=url_retrieve)(action_retrieve)
    action_list = decorators.action(detail=False, url_name=name_list, url_path=field.name)(action_list)

    # Apply Schema Decorators
    # This must be done after the action decorator is applied
    action_retrieve = utils.extend_schema(responses=serializer.child, filters=False)(action_retrieve)
    action_list = utils.extend_schema(responses=serializer, filters=False)(action_list)

    # Set Action Attributes on Class
    setattr(viewset, name_retrieve, action_retrieve)
    setattr(viewset, name_list, action_list)
