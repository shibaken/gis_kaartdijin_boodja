"""Kaartdijin Boodja Catalogue Django Application Notification Models."""


# Third-Party
from django.db import models

# Local
from . import catalogue_entries


class NotificationType(models.IntegerChoices):
    """Enumeration for a Notification Type."""
    ON_APPROVE = 1
    ON_LOCK = 2
    BOTH = 3


class EmailNotification(models.Model):
    """Model for an Email Notification."""
    name = models.TextField()
    type = models.IntegerField(choices=NotificationType.choices)  # noqa: A003
    email = models.TextField()
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="email_notifications",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Email Notification Model Metadata."""
        verbose_name = "Email Notification"
        verbose_name_plural = "Email Notifications"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"


class WebhookNotification(models.Model):
    """Model for a Webhook Notification."""
    name = models.TextField()
    type = models.IntegerField(choices=NotificationType.choices)  # noqa: A003
    url = models.URLField()
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="webhook_notifications",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Webhook Notification Model Metadata."""
        verbose_name = "Webhook Notification"
        verbose_name_plural = "Webhook Notifications"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
