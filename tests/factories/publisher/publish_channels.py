"""Model Factories for the Publisher Publish Channel Model."""


# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.publisher import models
from tests.factories.publisher import workspaces


class CDDPPublishChannelFactory(factory.django.DjangoModelFactory):
    """Factory for a CDDP Publish Channel."""
    description = factory.Faker("paragraph")
    mode = factory.fuzzy.FuzzyChoice(models.publish_channels.CDDPPublishChannelMode)
    frequency = factory.fuzzy.FuzzyChoice(models.publish_channels.PublishChannelFrequency)
    path = factory.Faker("tests")  # Hardcode for unit tests

    class Meta:
        """Publish Channel Factory Metadata."""
        model = models.publish_channels.CDDPPublishChannel


class GeoServerPublishChannelFactory(factory.django.DjangoModelFactory):
    """Factory for a GeoServer Publish Channel."""
    description = factory.Faker("paragraph")
    mode = factory.fuzzy.FuzzyChoice(models.publish_channels.GeoServerPublishChannelMode)
    frequency = factory.fuzzy.FuzzyChoice(models.publish_channels.PublishChannelFrequency)
    workspace = factory.SubFactory(workspaces.WorkspaceFactory)

    class Meta:
        """Publish Channel Factory Metadata."""
        model = models.publish_channels.GeoServerPublishChannel
