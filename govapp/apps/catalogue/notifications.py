"""Kaartdijin Boodja Catalogue Django Application Notification Utilities."""


# Standard
import shutil

# Local
from . import emails
from . import sharepoint
from . import webhooks
from ..accounts import utils
from ... import gis

# Typing
from typing import TYPE_CHECKING

# Type Checking
if TYPE_CHECKING:
    from .models import catalogue_entries


def file_absorb_failure() -> None:
    """Sends notifications for a file absorption failure."""
    # Send Emails!
    emails.FileAbsorbFailEmail().send_to(
        *utils.all_administrators(),  # Send to all administrators
    )


def catalogue_entry_creation() -> None:
    """Sends notifications for a Catalogue Entry creation."""
    # Send Emails
    emails.CatalogueEntryCreatedEmail().send_to(
        *utils.all_administrators(),  # All administrators
    )


def catalogue_entry_update_success(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Sends notifications for a Catalogue Entry update success.

    Args:
        entry (catalogue_entries.CatalogueEntry): Catalogue Entry to notify for
    """
    # Send Emails
    emails.CatalogueEntryUpdateSuccessEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
        *entry.email_notifications(manager="on_new_data").all(),  # type: ignore[operator]
        *entry.email_notifications(manager="both").all(),  # type: ignore[operator]
    )

    # Retrieve the File from Storage
    filepath = sharepoint.SharepointStorage().get_from_url(url=entry.active_layer.file)

    # Convert Layer to GeoJSON
    geojson = gis.conversions.to_geojson(
        filepath=filepath,
        layer=entry.metadata.name,
    )

    # Send Webhook Posts
    webhooks.post_geojson(
        *entry.webhook_notifications(manager="on_new_data").all(),  # type: ignore[operator]
        geojson=geojson,
    )

    # Delete local temporary copy of file if we can
    shutil.rmtree(filepath.parent, ignore_errors=True)


def catalogue_entry_update_failure(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Sends notifications for a Catalogue Entry update failure.

    Args:
        entry (catalogue_entries.CatalogueEntry): Catalogue Entry to notify for
    """
    # Send Emails
    emails.CatalogueEntryUpdateFailEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
    )


def catalogue_entry_lock(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Sends notifications for a Catalogue Entry lock.

    Args:
        entry (catalogue_entries.CatalogueEntry): Catalogue Entry to notify for
    """
    # Send Emails
    emails.CatalogueEntryLockedEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
        *entry.email_notifications(manager="on_lock").all(),  # type: ignore[operator]
        *entry.email_notifications(manager="both").all(),  # type: ignore[operator]
    )
