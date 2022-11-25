"""Model Factories for the Catalogue Layer Symbology Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class LayerSymbologyFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Symbology."""
    name = factory.Sequence(lambda n: f"Layer Symbology {n + 1}")
    sld = factory.Faker("paragraph")

    class Meta:
        """Layer Symbology Factory Metadata."""
        model = models.layer_symbology.LayerSymbology
