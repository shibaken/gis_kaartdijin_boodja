"""Model Factories for the Publisher Publish Entry Model."""


# Standard
import random

# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.publisher import models
from tests.factories import accounts
from tests.factories.publisher import notifications


class PublishEntryFactory(factory.django.DjangoModelFactory):
    """Factory for a Publish Entry."""
    name = factory.Sequence(lambda n: f"Publish Entry {n + 1}")
    description = factory.Faker("paragraph")
    status = factory.fuzzy.FuzzyChoice(models.publish_entries.PublishEntryStatus)
    assigned_to = factory.SubFactory(accounts.users.UserFactory)

    email_notifications = factory.RelatedFactoryList(
        notifications.EmailNotificationFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="publish_entry",
    )
    webhook_notifications = factory.RelatedFactoryList(
        notifications.WebhookNotificationFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="publish_entry",
    )

    class Meta:
        """Publish Entry Factory Metadata."""
        model = models.publish_entries.PublishEntry
