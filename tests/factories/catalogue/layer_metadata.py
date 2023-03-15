"""Model Factories for the Catalogue Layer Metadata Model."""


# Standard
import datetime

# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class LayerMetadataFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Metadata."""
    created_at = factory.Faker("date_time_this_year", tzinfo=datetime.timezone.utc)

    class Meta:
        """Layer Metadata Factory Metadata."""
        model = models.layer_metadata.LayerMetadata
