"""Model Factories for the Catalogue Layer Attribute Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class LayerAttributeFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Attribute."""
    name = factory.Sequence(lambda n: f"Layer Attribute {n + 1}")
    type = factory.Faker("word")  # noqa: A003
    order = factory.Faker("pyint")

    class Meta:
        """Layer Attribute Factory Metadata."""
        model = models.layer_attributes.LayerAttribute
