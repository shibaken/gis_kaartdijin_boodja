"""Provides unit tests for the Accounts App URL Routing."""


# Third-Party
from django import test
import pytest

# Local
import factories


@pytest.mark.django_db()
def test_users_me_unauthenticated(
    client: test.Client,
) -> None:
    """Tests that the users `me` endpoint works correctly.

    Args:
        client (test.Client): Django test client fixture.
    """
    # Retrieve response (unauthenticated)
    response = client.get("/api/accounts/users/me/")

    # Assert response
    assert response.status_code == 200
    assert response.json() == {"id": None, "username": "", "groups": []}


@pytest.mark.django_db()
def test_users_me_authenticated(
    client: test.Client,
    user_factory: factories.accounts.users.UserFactory,
) -> None:
    """Tests that the users `me` endpoint works correctly.

    Args:
        client (test.Client): Django test client fixture.
        user_factory (UserFactory): PyTest fixture for a User.
    """
    # Retrieve response (authenticated)
    user = user_factory.create()
    client.force_login(user)
    response = client.get("/api/accounts/users/me/")

    # Assert response
    assert response.status_code == 200
    assert response.json() == {"id": user.id, "username": user.username, "groups": [g.id for g in user.groups.all()]}
