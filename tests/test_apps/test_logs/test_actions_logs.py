"""Provides unit tests for the Actions Logs Workflow."""


# Third-Party
from django import conf
from django import test
from django.contrib.auth import models as auth_models
import freezegun
import pytest
from rest_framework import status

# Local
import factories
from govapp.apps.catalogue import models


@pytest.mark.django_db()
@freezegun.freeze_time("2022-12-17")
def test_flow(
    client: test.Client,
    catalogue_entry_factory: factories.catalogue.catalogue_entries.CatalogueEntryFactory,
    user_factory: factories.accounts.users.UserFactory,
) -> None:
    """Tests that the endpoints work correctly.

    Args:
        client (test.Client): Django test client fixture.
        catalogue_entry_factory (CatalogueEntryFactory): PyTest fixture for a
            Catalogue Entry factory.
        user_factory (UserFactory): PyTest fixture for a User factory.
    """
    # Create Catalogue Entry
    # Ensure the Catalogue Entry starts Unlocked (Draft)
    entry = catalogue_entry_factory.create()
    assert isinstance(entry, models.catalogue_entries.CatalogueEntry)
    entry.status = models.catalogue_entries.CatalogueEntryStatus.DRAFT
    entry.save()

    # Ensure the Assigned To User is in the Catalogue Editors Group but NOT the
    # Administrators Group. Also ensure the Assigned To User is also in the
    # Catalogue Entry's editors
    assert isinstance(entry.assigned_to, auth_models.User)
    entry.assigned_to.groups.add(conf.settings.GROUP_CATALOGUE_EDITOR_ID)
    entry.assigned_to.groups.remove(conf.settings.GROUP_ADMINISTRATOR_ID)
    entry.editors.add(entry.assigned_to)
    entry.save()

    # Create a User
    # Ensure the user is an Administrator so it can do anything.
    user = user_factory.create()
    assert isinstance(user, auth_models.User)
    user.groups.add(conf.settings.GROUP_ADMINISTRATOR_ID)
    user.save()

    # Authenticate
    client.force_login(user)

    # Now, perform some actions on the Catalogue Entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/lock/"
    ).status_code == status.HTTP_204_NO_CONTENT
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/unlock/"
    ).status_code == status.HTTP_204_NO_CONTENT
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/unassign/"
    ).status_code == status.HTTP_204_NO_CONTENT
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/assign/{entry.assigned_to.pk}/"
    ).status_code == status.HTTP_204_NO_CONTENT
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/decline/"
    ).status_code == status.HTTP_204_NO_CONTENT

    # Now, check the Actions Logs
    assert client.get(
        path=f"/api/catalogue/entries/{entry.pk}/logs/actions/"
    ).json()["results"] == [
        {
            "id": 1,
            "who": user.pk,
            "what": "Catalogue entry was locked",
            "when": "2022-12-17T00:00:00Z",  # Time is frozen
        },
        {
            "id": 2,
            "who": user.pk,
            "what": "Catalogue entry was unlocked",
            "when": "2022-12-17T00:00:00Z",  # Time is frozen
        },
        {
            "id": 3,
            "who": user.pk,
            "what": "Catalogue entry was unassigned",
            "when": "2022-12-17T00:00:00Z",  # Time is frozen
        },
        {
            "id": 4,
            "who": user.pk,
            "what": f"Catalogue entry was assigned to {entry.assigned_to} (id: {entry.assigned_to.pk})",
            "when": "2022-12-17T00:00:00Z",  # Time is frozen
        },
        {
            "id": 5,
            "who": user.pk,
            "what": "Catalogue entry was declined",
            "when": "2022-12-17T00:00:00Z",  # Time is frozen
        },
    ]
