"""Provides unit tests for the Catalogue application mixins."""


# Third-Party
from django import http
from django.db import models
import pytest
from rest_framework import request
from rest_framework import serializers
from rest_framework import viewsets

# Local
from govapp.apps.catalogue import mixins


def test_choices_mixin_actions() -> None:
    """Tests the functionality of the Choices Mixin for ViewSets."""
    # Create Test Model
    # This Test Model contains a single choices field for testing the mixin
    class TestModel(models.Model):  # noqa: DJ08
        example = models.IntegerField(choices=[(1, "A"), (2, "B"), (3, "C")])

        class Meta:
            app_label = "tests"

    # Create Test Serializer
    # This Test Model Serializer just serializes the example choice field
    class TestModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = TestModel
            fields = ("example", )

    # Create Test ViewSet
    # This Test Model ViewSet subclasses the Choices Mixin for testing
    class TestModelViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
        queryset = TestModel.objects.all()
        serializer_class = TestModelSerializer

    # Instantiate ViewSet
    # The ViewSet is instantiated with an empty request as it is required
    # by the constructor method signature
    viewset = TestModelViewSet(request=request.Request(http.HttpRequest()))

    # Assert that only two extra actions were created
    assert len(viewset.get_extra_actions()) == 2

    # Assert retrieving choices primary keys that exist work
    assert viewset.example_retrieve(request=None, pk="1").data == {"id": 1, "label": "A"}  # type: ignore[attr-defined]
    assert viewset.example_retrieve(request=None, pk="2").data == {"id": 2, "label": "B"}  # type: ignore[attr-defined]
    assert viewset.example_retrieve(request=None, pk="3").data == {"id": 3, "label": "C"}  # type: ignore[attr-defined]

    # Assert retrieving choices primary keys that do not exist raise 404
    with pytest.raises(http.Http404):
        assert viewset.example_retrieve(request=None, pk=4)  # type: ignore[attr-defined]

    # Assert the result of listing all choices
    assert viewset.example_list(request=None).data["results"] == [  # type: ignore[attr-defined]
        {"id": 1, "label": "A"},
        {"id": 2, "label": "B"},
        {"id": 3, "label": "C"},
    ]
