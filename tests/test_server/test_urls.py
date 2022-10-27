"""Provides unit tests for the Django URL routing."""


# Third-Party
from django import test


def test_admin_unauthorized(client: test.Client) -> None:
    """Tests that the admin panel requires auth.

    Args:
        client (test.Client): Django test client fixture.
    """
    # Retrieve response
    response = client.get("/admin/")

    # Assert status code
    assert response.status_code == 302


def test_admin_authorized(admin_client: test.Client) -> None:
    """Tests that the admin panel is accessible.

    Args:
        admin_client (test.Client): Django admin test client fixture.
    """
    # Retrieve response
    response = admin_client.get("/admin/")

    # Assert status code
    assert response.status_code == 200
