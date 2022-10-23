"""Kaartdijin Boodja Catalogue Django Application Layer Symbology Models."""


# Third-Party
from django.db import models

# Local
from . import layer_submissions


class LayerSymbology(models.Model):
    """Model for a Layer Symbology."""
    name = models.TextField()
    file = models.URLField()
    layer = models.OneToOneField(
        layer_submissions.LayerSubmission,
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
