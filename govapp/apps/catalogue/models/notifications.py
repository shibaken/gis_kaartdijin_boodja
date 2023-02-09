"""Kaartdijin Boodja Catalogue Django Application Notification Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.common import utils
from govapp.apps.catalogue.models import catalogue_entries


class EmailNotificationType(models.IntegerChoices):
    """Enumeration for an Email Notification Type."""
    ON_NEW_DATA = 1
    ON_LOCK = 2
    BOTH = 3


class WebhookNotificationType(models.IntegerChoices):
    """Enumeration for a Webhook Notification Type."""
    ON_NEW_DATA = 1


@reversion.register()
class EmailNotification(mixins.RevisionedMixin):
    """Model for an Email Notification."""
    name = models.TextField()
    type = models.IntegerField(choices=EmailNotificationType.choices)  # noqa: A003
    email = models.TextField()
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="email_notifications",
        on_delete=models.CASCADE,
    )

    # Custom Managers
    # These managers are required so that the reverse relationship on the
    # Catalogue Entries (i.e., `catalogue_entry.email_notifications`) can be
    # easily filtered without knowing/importing the `EmailNotificationType`
    # implementation detail (which in this case would be a circular import).
    # These managers allow usage such as:
    # `catalogue_entry.email_notifications(manager="on_lock").all()`.
    objects = models.Manager()
    on_new_data = utils.filtered_manager(type=EmailNotificationType.ON_NEW_DATA)  # type: ignore
    on_lock = utils.filtered_manager(type=EmailNotificationType.ON_LOCK)  # type: ignore
    both = utils.filtered_manager(type=EmailNotificationType.BOTH)  # type: ignore

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


@reversion.register()
class WebhookNotification(mixins.RevisionedMixin):
    """Model for a Webhook Notification."""
    name = models.TextField()
    type = models.IntegerField(choices=WebhookNotificationType.choices)  # noqa: A003
    url = models.URLField()
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry,
        related_name="webhook_notifications",
        on_delete=models.CASCADE,
    )

    # Custom Managers
    # These managers are required so that the reverse relationship on the
    # Catalogue Entries (i.e., `catalogue_entry.webhook_notifications`) can be
    # easily filtered without knowing/importing the `WebhookNotificationType`
    # implementation detail (which in this case would be a circular import).
    # These managers allow usage such as:
    # `catalogue_entry.webhook_notifications(manager="on_lock").all()`.
    objects = models.Manager()
    on_new_data = utils.filtered_manager(type=WebhookNotificationType.ON_NEW_DATA)  # type: ignore

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
