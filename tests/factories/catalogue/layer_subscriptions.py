"""Model Factories for the Catalogue Layer Subscription Model."""


# Standard
import datetime

# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.catalogue import models


class LayerSubscriptionFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Subscription."""
    name = factory.Sequence(lambda n: f"Layer Subscription {n + 1}")
    url = factory.Faker("uri")
    frequency = factory.Faker("time_delta")
    status = factory.fuzzy.FuzzyChoice(models.layer_subscriptions.LayerSubscriptionStatus)
    subscribed_at = factory.Faker("date_time_this_year", tzinfo=datetime.timezone.utc)

    class Meta:
        """Layer Subscription Factory Metadata."""
        model = models.layer_subscriptions.LayerSubscription
