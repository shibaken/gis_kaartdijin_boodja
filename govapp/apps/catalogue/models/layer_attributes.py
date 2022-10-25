"""Kaartdijin Boodja Catalogue Django Application Layer Attribute Models."""


# Third-Party
from django.db import models

# Local
from . import layer_submissions


class LayerAttributeType(models.IntegerChoices):
    """Enumeration for a Layer Attribute Type."""
    SHORT = 1
    LONG = 2
    FLOAT = 3
    DOUBLE = 4
    TEXT = 5
    DATE = 6
    BLOB = 7
    OBJECT_ID = 8
    GLOBAL_ID = 9
    GEOMETRY = 10


class LayerAttribute(models.Model):
    """Model for a Layer Attribute."""
    name = models.TextField()
    type = models.IntegerField(choices=LayerAttributeType.choices)  # noqa: A003
    order = models.PositiveIntegerField()
    layer = models.ForeignKey(
        layer_submissions.LayerSubmission,
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
