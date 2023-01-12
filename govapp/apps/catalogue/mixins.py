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
from reversion import models as reversion_models
from reversion_rest_framework import mixins as reversion_mixins
import reversion

# Typing
from typing import Any, Iterable, Optional


class HistoryMixin(reversion_mixins.HistoryMixin):
    """Retrieve and list the Django Reversion versions for this model."""

    def _build_serializer(
        self,
        instance_class: type,
        queryset: models.QuerySet,
        many: bool = False,
    ) -> serializers.Serializer:
        """Builds a serializer for the Django Reversion versions.

        Args:
            instance_class (type): Instance class to build serializer for.
            queryset (models.QuerySet): Queryset to build serializer for.
            many (bool): Whether this is a `many` serializer.

        Returns:
            serializers.Serializer: The built serializer.
        """
        # Build Serializer
        serializer = super()._build_serializer(instance_class, queryset, many)

        # Construct Patch Function
        def get_field_dict(obj: reversion_models.Version) -> dict[str, Any]:
            # Remove "_id" suffix from field names and return
            return {k.rsplit("_id")[0]: v for (k, v) in obj.field_dict.items()}

        # Retrieve Child Serializer if Applicable
        # This is required because if `many == True` then the serializer is
        # actually a `ListSerializer`, and we want to patch the child.
        s = serializer if not many else serializer.child

        # Patch Serializer
        s.get_field_dict = get_field_dict

        # Return Serializer
        return serializer  # type: ignore


class RevisionedMixin(models.Model):
    """Django model tracked by Django Reversion through the save method."""

    class Meta:
        """Revisioned Mixin Metadata."""
        abstract = True

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Saves the Django model in the database.

        Args:
            force_insert (bool): Whether to force insert.
            force_update (bool): Whether to force update.
            using (Optional[str]): Database to use.
            update_fields (Optional[Iterable[str]]): Fields to update.
            **kwargs (Any): Extra keyword arguments for Django Reversion.
        """
        # Create Revision
        with reversion.create_revision():
            # Set Version User and Comment
            reversion.set_user(kwargs.pop("version_user", None))
            reversion.set_comment(kwargs.pop("version_comment", ""))

            # Save the Model
            return super().save(force_insert, force_update, using, update_fields)


class MultipleSerializersMixin:
    """Allows for multiple serializers for different actions on a viewset."""

    # The inheriting class must have the following defined
    serializer_classes: dict[str, type[serializers.Serializer]]
    action: str

    def get_serializer_class(self) -> type[serializers.Serializer]:
        """Retrieves the serializer class.

        Returns:
            type[serializers.Serializer]: Retrieved serializer class.
        """
        # Retrieve Serializer Class and Return
        return self.serializer_classes.get(
            self.action,
            super().get_serializer_class(),  # type: ignore[misc]
        )


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
