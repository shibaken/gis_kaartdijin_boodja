"""Provides unit tests for the Django WSGI module."""


# Third-Party
from django.core.handlers import wsgi

# Local
from govapp import wsgi as wsgi_module


def test_wsgi_application_exists() -> None:
    """Tests that the WSGI handler is exposed correctly."""
    # Assert
    assert hasattr(wsgi_module, "application")
    assert isinstance(wsgi_module.application, wsgi.WSGIHandler)
