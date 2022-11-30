"""Provides configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
    1. https://docs.python.org/3/library/doctest.html
    2. https://docs.pytest.org/en/latest/doctest.html
"""


# Third-Party
import pytest
import pytest_django.fixtures
import pytest_factoryboy

# Local
import tests.factories


# Register Factories
pytest_factoryboy.register(tests.factories.accounts.users.UserFactory)
pytest_factoryboy.register(tests.factories.catalogue.catalogue_entries.CatalogueEntryFactory)
pytest_factoryboy.register(tests.factories.catalogue.custodians.CustodianFactory)
pytest_factoryboy.register(tests.factories.catalogue.layer_attributes.LayerAttributeFactory)
pytest_factoryboy.register(tests.factories.catalogue.layer_metadata.LayerMetadataFactory)
pytest_factoryboy.register(tests.factories.catalogue.layer_submissions.LayerSubmissionFactory)
pytest_factoryboy.register(tests.factories.catalogue.layer_subscriptions.LayerSubscriptionFactory)
pytest_factoryboy.register(tests.factories.catalogue.layer_symbology.LayerSymbologyFactory)
pytest_factoryboy.register(tests.factories.catalogue.notifications.EmailNotificationFactory)
pytest_factoryboy.register(tests.factories.catalogue.notifications.WebhookNotificationFactory)


@pytest.fixture(autouse=True)
def debug(settings: pytest_django.fixtures.SettingsWrapper) -> None:  # noqa: PT004
    """Sets proper DEBUG and TEMPLATE debug mode for coverage.

    Args:
        settings (fixtures.SettingsWrapper): Pytest Django settings fixture.
    """
    # Set debug flag to false
    settings.DEBUG = False

    # Set templates to debug mode
    for template in settings.TEMPLATES:
        template["OPTIONS"]["debug"] = True
