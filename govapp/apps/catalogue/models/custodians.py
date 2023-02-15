"""Kaartdijin Boodja Catalogue Django Application Custodian Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins


@reversion.register()
class Custodian(mixins.RevisionedMixin):
    """Model for a Custodian."""
    name = models.TextField()
    contact_name = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.TextField(blank=True)

    class Meta:
        """Custodian Model Metadata."""
        verbose_name = "Custodian"
        verbose_name_plural = "Custodians"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
