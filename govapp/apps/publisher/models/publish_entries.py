"""Kaartdijin Boodja Publisher Django Application Publish Entry Models."""


# Standard
import logging

# Third-Party
from django.contrib import auth
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue.models import catalogue_entries

# Typing
from typing import TYPE_CHECKING

# Type Checking
if TYPE_CHECKING:
    from govapp.apps.publisher.models import notifications
    from govapp.apps.publisher.models import publish_channels


# Shortcuts
UserModel = auth.get_user_model()

# Logging
log = logging.getLogger(__name__)


class PublishEntryStatus(models.IntegerChoices):
    """Enumeration for a Publish Entry Status."""
    LOCKED = 1
    UNLOCKED = 2


@reversion.register()
class PublishEntry(mixins.RevisionedMixin):
    """Model for a Publish Entry."""
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(choices=PublishEntryStatus.choices, default=PublishEntryStatus.LOCKED)
    updated_at = models.DateTimeField(auto_now=True)
    editors = models.ManyToManyField(UserModel, blank=True)
    assigned_to = models.ForeignKey(
        UserModel,
        default=None,
        blank=True,
        null=True,
        related_name="assigned_publish",
        on_delete=models.SET_NULL,
    )
    catalogue_entry = models.OneToOneField(
        catalogue_entries.CatalogueEntry,
        related_name="publish_entry",
        on_delete=models.CASCADE,
    )

    # Type Hints for Reverse Relations
    # These aren't exactly right, but are useful for catching simple mistakes.
    cddp_channel: "publish_channels.CDDPPublishChannel"
    geoserver_channel: "publish_channels.GeoServerPublishChannel"
    email_notifications: "models.Manager[notifications.EmailNotification]"
    webhook_notifications: "models.Manager[notifications.WebhookNotification]"

    class Meta:
        """Publish Entry Model Metadata."""
        verbose_name = "Publish Entry"
        verbose_name_plural = "Publish Entries"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    def publish(self, force: bool = False) -> None:
        """Publishes Catalogue Entry to all channels if applicable.

        Args:
            force (bool): Whether to force publish to all channels.
        """
        # Log
        log.info(f"Publishing '{self.catalogue_entry}' - '{self}' ({force=})")

        # Check for Channel
        if hasattr(self, "cddp_channel"):
            # Publish!
            self.cddp_channel.publish()

        # Check for Channel
        if hasattr(self, "geoserver_channel"):
            # Publish!
            self.geoserver_channel.publish()
