"""Kaartdijin Boodja Catalogue Django Application Layer Submission Models."""


# Third-Party
from django.db import models

# Local
from . import catalogue_entries


class LayerSubmissionStatus(models.IntegerChoices):
    """Enumeration for a Layer Submission Status."""
    SUBMITTED = 1
    ACCEPTED = 2
    DECLINED = 3


class LayerSubmission(models.Model):
    """Model for a Layer Submission."""
    name = models.TextField()
    description = models.TextField()
    file = models.URLField()
    status = models.IntegerField(choices=LayerSubmissionStatus.choices, default=LayerSubmissionStatus.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="layers",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Layer Submission Model Metadata."""
        verbose_name = "Layer Submission"
        verbose_name_plural = "Layer Submissions"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
