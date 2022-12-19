"""Provides unit tests for the Communications Logs Workflow."""


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
    entry = catalogue_entry_factory.create()
    assert isinstance(entry, models.catalogue_entries.CatalogueEntry)

    # Create a User
    # Ensure the user is not in any groups, so it has no special permissions.
    user = user_factory.create()
    assert isinstance(user, auth_models.User)
    user.groups.remove(conf.settings.GROUP_ADMINISTRATOR_ID)
    user.groups.remove(conf.settings.GROUP_CATALOGUE_EDITOR_ID)
    user.save()

    # Authenticate
    client.force_login(user)

    # Create Communications Log Entry
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/",
        data={
            "type": 1,
            "to": "to@example.com",
            "cc": "cc@example.com",
            "from": "from@example.com",
            "subject": "example subject",
            "text": "example text",
        },
        content_type="application/json",
    ).status_code == status.HTTP_201_CREATED

    # Attach a File
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/1/file/",
        data={
            "name": "example name",
            "description": "example description",
            "file": open(__file__),  # Upload self
        },
    ).status_code == status.HTTP_201_CREATED

    # Define Expected Response
    expected_response = {
        "id": 1,
        "type": 1,
        "created_at": "2022-12-17T00:00:00Z",  # Time is frozen
        "to": "to@example.com",
        "cc": "cc@example.com",
        "from": "from@example.com",
        "subject": "example subject",
        "text": "example text",
        "user": user.pk,
        "documents": [
            {
                "id": 1,
                "name": "example name",
                "description": "example description",
                "file": "http://testserver/documents/test_communications_logs.py",
                "uploaded_at": "2022-12-17T00:00:00Z",  # Time is frozen
            }
        ]
    }

    # Retrieve Entries (List)
    assert client.get(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/",
    ).json()["results"] == [expected_response]  # Paginated list

    # Retrieve Entry (Detail)
    assert client.get(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/1/",
    ).json() == expected_response

    # Create another User
    # Ensure the user is not in any groups, so it has no special permissions.
    user = user_factory.create()
    assert isinstance(user, auth_models.User)
    user.groups.remove(conf.settings.GROUP_ADMINISTRATOR_ID)
    user.groups.remove(conf.settings.GROUP_CATALOGUE_EDITOR_ID)
    user.save()

    # Authenticate
    client.force_login(user)

    # Attach a File (Fail)
    assert client.post(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/1/file/",
        data={
            "name": "another example name",
            "description": "another example description",
            "file": open(__file__),  # Upload self
        },
    ).status_code == status.HTTP_403_FORBIDDEN

    # Retrieve Entries (List)
    assert client.get(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/",
    ).json()["results"] == [expected_response]  # Paginated list

    # Retrieve Entry (Detail)
    assert client.get(
        path=f"/api/catalogue/entries/{entry.pk}/logs/communications/1/",
    ).json() == expected_response
