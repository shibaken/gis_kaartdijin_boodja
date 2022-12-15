"""Kaartdijin Boodja Catalogue Django Application Layer Attribute Models."""


# Third-Party
from django.db import models
import reversion

# Local
from . import catalogue_entries
from .. import mixins


@reversion.register()
class LayerAttribute(mixins.RevisionedMixin):
    """Model for a Layer Attribute."""
    name = models.TextField()
    type = models.TextField()  # noqa: A003
    order = models.PositiveIntegerField()
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="attributes",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Layer Attribute Model Metadata."""
        verbose_name = "Layer Attribute"
        verbose_name_plural = "Layer Attributes"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
