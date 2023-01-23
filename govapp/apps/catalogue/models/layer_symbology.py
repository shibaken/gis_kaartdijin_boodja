"""Kaartdijin Boodja Catalogue Django Application Layer Symbology Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp import gis
from govapp.common import mixins
from govapp.apps.catalogue import validators
from govapp.apps.catalogue.models import catalogue_entries


@reversion.register()
class LayerSymbology(mixins.RevisionedMixin):
    """Model for a Layer Symbology."""
    name = models.TextField()
    sld = models.TextField(validators=[validators.validate_xml, validators.validate_sld])
    catalogue_entry = models.OneToOneField(
        catalogue_entries.CatalogueEntry,
        related_name="symbology",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Layer Symbology Model Metadata."""
        verbose_name = "Layer Symbology"
        verbose_name_plural = "Layer Symbologies"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    def publish(self) -> None:
        """Publishes the style to GeoServer."""
        # Push Style to GeoServer
        gis.geoserver.GeoServer().upload_style(
            workspace=self.catalogue_entry.workspace.name,
            layer=self.catalogue_entry.metadata.name,
            name=self.name,
            sld=self.sld,
        )
