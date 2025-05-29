"""Kaartdijin Boodja Catalogue Django Application Layer Symbology Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue import validators
from govapp.apps.catalogue.models import catalogue_entries


@reversion.register()
class LayerSymbology(mixins.RevisionedMixin):
    """Model for a Layer Symbology."""
    sld = models.TextField(validators=[validators.validate_xml, validators.validate_sld], blank=True, default='')
    use_raw = models.BooleanField(default=False)  # Ref: https://docs.geoserver.org/main/en/user/rest/api/styles.html#raw
                                                  # The raw parameter specifies whether to forgo parsing and encoding of the uploaded style content. When set to “true” the style payload will be streamed directly to GeoServer configuration. Use this setting if the content and formatting of the style is to be preserved exactly. Use this setting with care as it may result in an invalid and unusable style. The default is “false”.
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
        return f"ID:{self.id} {self.name}"

    @property
    def name(self) -> str:
        """Proxies the Catalogue Entry's name to this model.

        Returns:
            str: Name of the Catalogue Entry.
        """
        # Retrieve and Return
        return self.catalogue_entry.name
