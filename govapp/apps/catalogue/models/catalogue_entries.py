"""Kaartdijin Boodja Catalogue Django Application Catalogue Entry Models."""


# Third-Party
from django.contrib import auth
from django.db import models

# Local
from . import custodians
from .. import utils

# Typing
from typing import TYPE_CHECKING

# Type Checking
if TYPE_CHECKING:
    from . import layer_submissions


# Shortcuts
UserModel = auth.get_user_model()


class CatalogueEntryStatus(models.IntegerChoices):
    """Enumeration for a Catalogue Entry Status."""
    NEW_DRAFT = 1
    LOCKED = 2
    DECLINED = 3
    DRAFT = 4
    PENDING = 5


class CatalogueEntry(models.Model):
    """Model for a Catalogue Entry."""
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(choices=CatalogueEntryStatus.choices, default=CatalogueEntryStatus.NEW_DRAFT)
    updated_at = models.DateTimeField(auto_now=True)
    custodian = models.ForeignKey(
        custodians.Custodian,
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

    @property
    def active_layer(self) -> "layer_submissions.LayerSubmission":
        """Retrieves the currently active layer.

        Returns:
            layer_submissions.LayerSubmission: The currently active layer.
        """
        # Retrieve Active Layer
        active_layer = self.layers.filter(is_active=True).last()

        # Check
        assert active_layer is not None, f"{repr(self)} has no active layer"  # noqa: S101

        # Return
        return active_layer

    def is_locked(self) -> bool:
        """Determines whether the Catalogue Entry is locked.

        Returns:
            bool: Whether the Catalogue Entry is locked.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.LOCKED

    def is_pending(self) -> bool:
        """Determines whether the Catalogue Entry is locked (pending).

        Returns:
            bool: Whether the Catalogue Entry is locked (pending).
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.PENDING

    def is_declined(self) -> bool:
        """Determines whether the Catalogue Entry is declined.

        Returns:
            bool: Whether the Catalogue Entry is declined.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.DECLINED

    def is_unlocked(self) -> bool:
        """Determines whether the Catalogue Entry is unlocked.

        Returns:
            bool: Whether the Catalogue Entry is unlocked.
        """
        # Check and Return
        return self.status in (CatalogueEntryStatus.DRAFT, CatalogueEntryStatus.NEW_DRAFT)

    def is_new(self) -> bool:
        """Determines whether the Catalogue Entry is a new draft.

        Returns:
            bool: Whether the Catalogue Entry is a new draft.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.NEW_DRAFT

    def lock(self) -> None:
        """Locks the Catalogue Entry."""
        # Check Catalogue Entry
        if self.is_unlocked():
            # Check if Catalogue Entry is new
            if self.is_new():
                # Lock the currently active layer
                self.active_layer.accept()

            # Calculate the attributes hash
            attributes_hash = utils.attributes_hash(self.attributes.all())

            # Compare attributes hash with current active layer submission
            if self.active_layer.hash == attributes_hash:
                # Set Catalogue Entry to Locked
                self.status = CatalogueEntryStatus.LOCKED

            else:
                # Set Catalogue Entry to Pending
                self.status = CatalogueEntryStatus.PENDING

            # Save the Catalogue Entry
            self.save()

    def unlock(self) -> None:
        """Unlocks the Catalogue Entry."""
        # Check Catalogue Entry
        if self.is_locked() or self.is_pending():
            # Set Catalogue Entry to Draft
            self.status = CatalogueEntryStatus.DRAFT
            self.save()
