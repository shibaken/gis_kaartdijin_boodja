"""Provides unit tests for the Catalogue model string representations."""


# Third-Party
import pytest

# Local
from govapp.apps.catalogue import models
import factories


@pytest.mark.django_db()
def test_model_strings(
    catalogue_entry_factory: factories.catalogue.catalogue_entries.CatalogueEntryFactory,
    layer_subscription_factory: factories.catalogue.layer_subscriptions.LayerSubscriptionFactory,
) -> None:
    """Tests the string representations of the models.

    As a byproduct, this also tests that the factories are working.

    Args:
        catalogue_entry_factory (CatalogueEntryFactory): PyTest fixture for a
            Catalogue Entry factory.
        layer_subscription_factory (LayerSubscriptionFactory): PyTest fixture
            for a Layer Subscription Factory.
    """
    # Create Catalogue Entry
    catalogue_entry = catalogue_entry_factory.create()

    # Assert Catalogue Entry str() Representation
    assert isinstance(catalogue_entry, models.catalogue_entries.CatalogueEntry)
    assert str(catalogue_entry) == catalogue_entry.name

    # Assert Custodian str() Representation
    custodian = catalogue_entry.custodian
    assert isinstance(custodian, models.custodians.Custodian)
    assert str(custodian) == custodian.name

    # Assert Layer Submission str() Representation
    layer_submission = catalogue_entry.active_layer
    assert isinstance(layer_submission, models.layer_submissions.LayerSubmission)
    assert str(layer_submission) == layer_submission.name

    # Assert Layer Attribute str() Representation
    layer_attribute = catalogue_entry.attributes.first()
    assert isinstance(layer_attribute, models.layer_attributes.LayerAttribute)
    assert str(layer_attribute) == layer_attribute.name

    # Assert Layer Metadata str() Representation
    layer_metadata = catalogue_entry.metadata
    assert isinstance(layer_metadata, models.layer_metadata.LayerMetadata)
    assert str(layer_metadata) == layer_metadata.name

    # Assert Layer Symbology str() Representation
    layer_symbology = catalogue_entry.symbology
    assert isinstance(layer_symbology, models.layer_symbology.LayerSymbology)
    assert str(layer_symbology) == layer_symbology.name

    # Assert Layer Symbology str() Representation
    layer_symbology = catalogue_entry.symbology
    assert isinstance(layer_symbology, models.layer_symbology.LayerSymbology)
    assert str(layer_symbology) == layer_symbology.name

    # Assert Email Notification str() Representation
    email_notification = catalogue_entry.email_notifications.first()
    assert isinstance(email_notification, models.notifications.EmailNotification)
    assert str(email_notification) == email_notification.name

    # Assert Webhook Notification str() Representation
    webhook_notification = catalogue_entry.webhook_notifications.first()
    assert isinstance(webhook_notification, models.notifications.WebhookNotification)
    assert str(webhook_notification) == webhook_notification.name

    # Assert Email Notification str() Representation
    layer_subscription = layer_subscription_factory.create(catalogue_entry=catalogue_entry)
    assert isinstance(layer_subscription, models.layer_subscriptions.LayerSubscription)
    assert str(layer_subscription) == layer_subscription.name
