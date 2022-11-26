"""Provides unit tests for the Catalogue App Permissions."""


# Third-Party
from django import conf
from django import test
from django.contrib.auth import models as auth_models
import pytest
from rest_framework import status

# Local
import factories
from govapp.apps.catalogue import models
from govapp.apps.catalogue import serializers

# Typing
from typing import Any


@pytest.mark.django_db()
def test_flow_not_catalogue_editor(
    client: test.Client,
    catalogue_entry_factory: factories.catalogue.catalogue_entries.CatalogueEntryFactory,
) -> None:
    """Tests that the endpoints work correctly as non-catalogue editor.

    Args:
        client (test.Client): Django test client fixture.
        catalogue_entry_factory (CatalogueEntryFactory): PyTest fixture for a
            Catalogue Entry factory.
    """
    # Create Catalogue Entry
    entry = catalogue_entry_factory.create()
    assert isinstance(entry, models.catalogue_entries.CatalogueEntry)

    # Ensure the Assigned To User is NOT in the Catalogue Editors Group
    assert isinstance(entry.assigned_to, auth_models.User)
    entry.assigned_to.groups.remove(conf.settings.GROUP_CATALOGUE_EDITOR_ID)

    # Authenticate
    client.force_login(entry.assigned_to)

    # Render to JSON
    entry_json = serializers.catalogue_entries.CatalogueEntrySerializer(entry)
    entry_update_args: dict[str, Any] = {"data": entry_json.data, "content_type": "application/json"}

    # Nobody can create a catalogue entry
    assert client.post(
        path="/api/catalogue/entries/", **entry_update_args
    ).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Anyone can retrieve the catalogue entries and statuses
    assert client.get(
        path="/api/catalogue/entries/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/{entry.id}/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path="/api/catalogue/entries/status/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/status/{entry.status}/"
    ).status_code == status.HTTP_200_OK

    # Non catalogue editor users cannot unlock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/unlock/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non catalogue editor users cannot update the catalogue entry
    assert client.put(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non catalogue editor users cannot lock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/lock/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Get a Layer Attribute
    attr = entry.attributes.last()
    assert isinstance(attr, models.layer_attributes.LayerAttribute)

    # Render to JSON
    attr_json = serializers.layer_attributes.LayerAttributeSerializer(attr)
    attr_update_args: dict[str, Any] = {"data": attr_json.data, "content_type": "application/json"}

    # Anyone can retrieve the layer attributes
    assert client.get(
        path="/api/catalogue/layers/attributes/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_200_OK

    # Non catalogue editor users cannot update the attributes
    assert client.put(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non catalogue editor users cannot delete the attributes
    assert client.delete(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non catalogue editor users cannot create new attributes
    assert client.post(
        path="/api/catalogue/layers/attributes/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_flow_not_assigned_to(
    client: test.Client,
    catalogue_entry_factory: factories.catalogue.catalogue_entries.CatalogueEntryFactory,
) -> None:
    """Tests that the endpoints work correctly as non-assigned to user.

    Args:
        client (test.Client): Django test client fixture.
        catalogue_entry_factory (CatalogueEntryFactory): PyTest fixture for a
            Catalogue Entry factory.
    """
    # Create Catalogue Entry
    entry = catalogue_entry_factory.create()
    assert isinstance(entry, models.catalogue_entries.CatalogueEntry)

    # Ensure the User is in the Catalogue Editors Group
    assert isinstance(entry.assigned_to, auth_models.User)
    entry.assigned_to.groups.add(conf.settings.GROUP_CATALOGUE_EDITOR_ID)

    # Authenticate
    client.force_login(entry.assigned_to)

    # Ensure the User is NOT Assigned to this catalogue entry
    entry.assigned_to = None
    entry.save()

    # Render to JSON
    entry_json = serializers.catalogue_entries.CatalogueEntrySerializer(entry)
    entry_update_args: dict[str, Any] = {"data": entry_json.data, "content_type": "application/json"}

    # Nobody can create a catalogue entry
    assert client.post(
        path="/api/catalogue/entries/", **entry_update_args
    ).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Anyone can retrieve the catalogue entries and statuses
    assert client.get(
        path="/api/catalogue/entries/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/{entry.id}/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path="/api/catalogue/entries/status/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/status/{entry.status}/"
    ).status_code == status.HTTP_200_OK

    # Non assigned_to users cannot unlock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/unlock/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non assigned_to users cannot update the catalogue entry
    assert client.put(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non assigned_to users cannot lock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/lock/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Get a Layer Attribute
    attr = entry.attributes.last()
    assert isinstance(attr, models.layer_attributes.LayerAttribute)

    # Render to JSON
    attr_json = serializers.layer_attributes.LayerAttributeSerializer(attr)
    attr_update_args: dict[str, Any] = {"data": attr_json.data, "content_type": "application/json"}

    # Anyone can retrieve the layer attributes
    assert client.get(
        path="/api/catalogue/layers/attributes/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_200_OK

    # Non assigned to users cannot update the attributes
    assert client.put(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non assigned to users cannot delete the attributes
    assert client.delete(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Non assigned to users cannot create new attributes
    assert client.post(
        path="/api/catalogue/layers/attributes/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_flow_catalogue_editor_and_assigned(
    client: test.Client,
    catalogue_entry_factory: factories.catalogue.catalogue_entries.CatalogueEntryFactory,
) -> None:
    """Tests that the endpoints work correctly when fully authorized.

    Args:
        client (test.Client): Django test client fixture.
        catalogue_entry_factory (CatalogueEntryFactory): PyTest fixture for a
            Catalogue Entry factory.
    """
    # Create Catalogue Entry
    entry = catalogue_entry_factory.create()
    assert isinstance(entry, models.catalogue_entries.CatalogueEntry)

    # Ensure the Assigned To User is in the Catalogue Editors Group
    assert isinstance(entry.assigned_to, auth_models.User)
    entry.assigned_to.groups.add(conf.settings.GROUP_CATALOGUE_EDITOR_ID)

    # Authenticate
    client.force_login(entry.assigned_to)

    # Render to JSON
    entry_json = serializers.catalogue_entries.CatalogueEntrySerializer(entry)
    entry_update_args: dict[str, Any] = {"data": entry_json.data, "content_type": "application/json"}

    # Nobody can create a catalogue entry
    assert client.post(
        path="/api/catalogue/entries/",
        **entry_update_args,
    ).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Anyone can retrieve the catalogue entries and statuses
    assert client.get(
        path="/api/catalogue/entries/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/{entry.id}/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path="/api/catalogue/entries/status/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/entries/status/{entry.status}/"
    ).status_code == status.HTTP_200_OK

    # Authorized user can unlock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/unlock/"
    ).status_code == status.HTTP_204_NO_CONTENT

    # Authorized user can update the unlocked catalogue entry
    assert client.put(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_200_OK
    assert client.patch(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_200_OK

    # Authorized user can lock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/lock/"
    ).status_code == status.HTTP_204_NO_CONTENT

    # Authorized user cannot update the locked catalogue entry
    assert client.put(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/entries/{entry.id}/",
        **entry_update_args,
    ).status_code == status.HTTP_403_FORBIDDEN

    # Get a Layer Attribute
    attr = entry.attributes.last()
    assert isinstance(attr, models.layer_attributes.LayerAttribute)

    # Render to JSON
    attr_json = serializers.layer_attributes.LayerAttributeSerializer(attr)
    attr_update_args: dict[str, Any] = {"data": attr_json.data, "content_type": "application/json"}

    # Anyone can retrieve the layer attributes
    assert client.get(
        path="/api/catalogue/layers/attributes/"
    ).status_code == status.HTTP_200_OK
    assert client.get(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_200_OK

    # Authorized users cannot update the attributes if the catalogue entry is locked
    assert client.put(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN

    # Authorized users cannot delete the attributes if the catalogue entry is locked
    assert client.delete(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_403_FORBIDDEN

    # Authorized users cannot create new attributes if the catalogue entry is locked
    assert client.post(
        path="/api/catalogue/layers/attributes/",
        **attr_update_args
    ).status_code == status.HTTP_403_FORBIDDEN

    # Authorized user can unlock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/unlock/"
    ).status_code == status.HTTP_204_NO_CONTENT

    # Authorized users can update the attributes if the catalogue entry is unlocked
    assert client.put(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_200_OK
    assert client.patch(
        path=f"/api/catalogue/layers/attributes/{attr.id}/",
        **attr_update_args
    ).status_code == status.HTTP_200_OK

    # Authorized users can delete the attributes if the catalogue entry is unlocked
    assert client.delete(
        path=f"/api/catalogue/layers/attributes/{attr.id}/"
    ).status_code == status.HTTP_204_NO_CONTENT

    # Authorized users can create new attributes if the catalogue entry is unlocked
    assert client.post(
        path="/api/catalogue/layers/attributes/",
        **attr_update_args
    ).status_code == status.HTTP_201_CREATED

    # Authorized user can lock the catalogue entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.id}/lock/"
    ).status_code == status.HTTP_204_NO_CONTENT
