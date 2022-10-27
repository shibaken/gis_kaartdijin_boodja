"""Provides unit tests for the Catalogue model string representations."""


# Third-Party
import pytest

# Local
from govapp.apps.catalogue import models


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_catalogue_entry_str() -> None:
    """Tests the string representation of a Catalogue Entry."""
    # Retrieve Object
    instance = models.catalogue_entries.CatalogueEntry.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_layer_attribute_str() -> None:
    """Tests the string representation of a Layer Attribute."""
    # Retrieve Object
    instance = models.layer_attributes.LayerAttribute.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_layer_metadata_str() -> None:
    """Tests the string representation of a Layer Metadata."""
    # Retrieve Object
    instance = models.layer_metadata.LayerMetadata.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_layer_submission_str() -> None:
    """Tests the string representation of a Layer Submission."""
    # Retrieve Object
    instance = models.layer_submissions.LayerSubmission.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_layer_subscription_str() -> None:
    """Tests the string representation of a Layer Subscription."""
    # Retrieve Object
    instance = models.layer_subscriptions.LayerSubscription.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_layer_symbology_str() -> None:
    """Tests the string representation of a Layer Symbology."""
    # Retrieve Object
    instance = models.layer_symbology.LayerSymbology.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_email_notification_str() -> None:
    """Tests the string representation of an Email Notification."""
    # Retrieve Object
    instance = models.notifications.EmailNotification.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name


@pytest.mark.django_db()
@pytest.mark.usefixtures("db_fixtures")
def test_webhook_notification_str() -> None:
    """Tests the string representation of a Webhook Notification."""
    # Retrieve Object
    instance = models.notifications.WebhookNotification.objects.first()

    # Assert String Representation
    assert instance
    assert str(instance) == instance.name
