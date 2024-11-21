"""Kaartdijin Boodja Publisher Django Application Notification Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.common import utils
from govapp.apps.publisher.models import publish_entries


class EmailNotificationType(models.IntegerChoices):
    """Enumeration for an Email Notification Type."""
    ON_PUBLISH = 1
    ON_LOCK = 2
    BOTH = 3


@reversion.register()
class EmailNotification(mixins.RevisionedMixin):
    """Model for an Email Notification."""
    name = models.TextField()
    type = models.IntegerField(choices=EmailNotificationType.choices)  # noqa: A003
    email = models.TextField()
    active = models.BooleanField(default=True)
    publish_entry = models.ForeignKey(
        publish_entries.PublishEntry,
        related_name="email_notifications",
        on_delete=models.CASCADE,
    )

    # Custom Managers
    # These managers are required so that the reverse relationship on the
    # Publish Entries (i.e., `publish_entry.email_notifications`) can be
    # easily filtered without knowing/importing the `EmailNotificationType`
    # implementation detail (which in this case would be a circular import).
    # These managers allow usage such as:
    # `publish_entry.email_notifications(manager="on_lock").all()`.
    objects = models.Manager()
    on_publish = utils.filtered_manager(type=EmailNotificationType.ON_PUBLISH)  # type: ignore
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
        return f"{self.id}: {self.name}"
