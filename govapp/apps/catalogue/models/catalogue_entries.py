"""Kaartdijin Boodja Catalogue Django Application Catalogue Entry Models."""


# Third-Party
from django.contrib import auth
from django.db import models


# Shortcuts
UserModel = auth.get_user_model()  # TODO -> Does this work with SSO?


class CatalogueEntryStatus(models.IntegerChoices):
    """Enumeration for a Catalogue Entry Status."""
    DRAFT = 1
    LOCKED = 2
    CANCELLED = 3


class CatalogueEntry(models.Model):
    """Model for a Catalogue Entry."""
    name = models.TextField()
    description = models.TextField()
    active_layer = models.OneToOneField(
        "catalogue.LayerSubmission",
        related_name="+",  # No backwards relation
        on_delete=models.PROTECT,
    )
    status = models.IntegerField(choices=CatalogueEntryStatus.choices, default=CatalogueEntryStatus.DRAFT)
    updated_at = models.DateTimeField(auto_now=True)
    custodian = models.ForeignKey(
        UserModel,
        default=None,
        blank=True,
        null=True,
        related_name="custody",
        on_delete=models.SET_NULL,
    )
    assigned_to = models.ForeignKey(
        UserModel,
        default=None,
        blank=True,
        null=True,
        related_name="assigned",
        on_delete=models.SET_NULL,
    )

    class Meta:
        """Catalogue Entry Model Metadata."""
        verbose_name = "Catalogue Entry"
        verbose_name_plural = "Catalogue Entries"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
