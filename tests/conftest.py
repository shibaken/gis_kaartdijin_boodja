"""Provides configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
    1. https://docs.python.org/3/library/doctest.html
    2. https://docs.pytest.org/en/latest/doctest.html
"""


# Third-Party
from django.core import management
import pytest
from pytest_django import fixtures
from pytest_django import plugin


@pytest.fixture(autouse=True)
def debug(settings: fixtures.SettingsWrapper) -> None:  # noqa: PT004
    """Sets proper DEBUG and TEMPLATE debug mode for coverage.

    Args:
        settings (fixtures.SettingsWrapper): Pytest Django settings fixture.
    """
    # Set debug flag to false
    settings.DEBUG = False

    # Set templates to debug mode
    for template in settings.TEMPLATES:
        template["OPTIONS"]["debug"] = True


@pytest.fixture()
def db_fixtures(  # noqa: PT004
    django_db_setup: None,
    django_db_blocker: plugin._DatabaseBlocker,
    settings: fixtures.SettingsWrapper
) -> None:
    """Loads model test fixtures into the database.

    Args:
        django_db_setup (None): Pytest Django dependency.
        django_db_blocker (plugin._DatabaseBlocker): Pytest Django dependency.
        settings (fixtures.SettingsWrapper): Pytest Django settings fixture.
    """
    # Unblock Database
    with django_db_blocker.unblock():
        # Load Fixtures
        management.call_command("loaddata", *settings.FIXTURES)
