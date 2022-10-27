"""Provides unit tests for the Django ASGI module."""


# Third-Party
from django.core.handlers import asgi

# Local
from govapp import asgi as asgi_module


def test_asgi_application_exists() -> None:
    """Tests that the ASGI handler is exposed correctly."""
    # Assert
    assert hasattr(asgi_module, "application")
    assert isinstance(asgi_module.application, asgi.ASGIHandler)
