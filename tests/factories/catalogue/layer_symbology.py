"""Model Factories for the Catalogue Layer Symbology Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models
from govapp.gis.readers import base


class LayerSymbologyFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Symbology."""
    sld = base.DEFAULT_SLD

    class Meta:
        """Layer Symbology Factory Metadata."""
        model = models.layer_symbology.LayerSymbology
