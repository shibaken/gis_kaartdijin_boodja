"""Model Factories for the Publisher Publish Channel Model."""


# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.publisher import models


class CDDPPublishChannelFactory(factory.django.DjangoModelFactory):
    """Factory for a CDDP Publish Channel."""
    name = factory.Sequence(lambda n: f"CDDP Publish Channel {n + 1}")
    description = factory.Faker("paragraph")
    frequency = factory.fuzzy.FuzzyChoice(models.publish_channels.PublishChannelFrequency)

    class Meta:
        """Publish Channel Factory Metadata."""
        model = models.publish_channels.CDDPPublishChannel


class GeoServerPublishChannelFactory(factory.django.DjangoModelFactory):
    """Factory for a GeoServer Publish Channel."""
    name = factory.Sequence(lambda n: f"GeoServer Publish Channel {n + 1}")
    description = factory.Faker("paragraph")
    frequency = factory.fuzzy.FuzzyChoice(models.publish_channels.PublishChannelFrequency)

    class Meta:
        """Publish Channel Factory Metadata."""
        model = models.publish_channels.GeoServerPublishChannel
