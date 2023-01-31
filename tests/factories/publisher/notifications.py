"""Model Factories for the Publisher Notification Models."""


# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.publisher import models


class EmailNotificationFactory(factory.django.DjangoModelFactory):
    """Factory for an Email Notification."""
    name = factory.Sequence(lambda n: f"Email Notification {n + 1}")
    type = factory.fuzzy.FuzzyChoice(models.notifications.EmailNotificationType)  # noqa: A003
    email = factory.Faker("safe_email")

    class Meta:
        """Email Notification Factory Metadata."""
        model = models.notifications.EmailNotification


class WebhookNotificationFactory(factory.django.DjangoModelFactory):
    """Factory for an Webhook Notification."""
    name = factory.Sequence(lambda n: f"Webhook Notification {n + 1}")
    type = factory.fuzzy.FuzzyChoice(models.notifications.WebhookNotificationType)  # noqa: A003
    url = factory.Faker("uri")

    class Meta:
        """Webhook Notification Factory Metadata."""
        model = models.notifications.WebhookNotification
