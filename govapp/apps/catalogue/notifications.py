"""Notification Utilities."""


# Local
from . import emails
from ..accounts import utils

# Typing
from typing import TYPE_CHECKING

# Type Checking
if TYPE_CHECKING:
    from .models import catalogue_entries


def file_absorb_failure() -> None:
    """Notifies for..."""
    # Send Emails!
    emails.FileAbsorbFailEmail().send_to(
        *utils.all_administrators(),  # Send to all administrators
    )


def catalogue_entry_creation() -> None:
    """Notifies for..."""
    # Send Emails
    emails.CatalogueEntryCreatedEmail().send_to(
        *utils.all_administrators(),  # All administrators
    )


def catalogue_entry_update_success(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Notifies for..."""
    # Send Emails
    emails.CatalogueEntryUpdateSuccessEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
        *entry.email_notifications(manager="on_approve").all(),  # type: ignore[operator]
        *entry.email_notifications(manager="both").all(),  # type: ignore[operator]
    )


def catalogue_entry_update_failure(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Notifies for..."""
    # Send Emails
    emails.CatalogueEntryUpdateFailEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
        *entry.email_notifications(manager="on_approve").all(),  # type: ignore[operator]
        *entry.email_notifications(manager="both").all(),  # type: ignore[operator]
    )


def catalogue_entry_lock(entry: "catalogue_entries.CatalogueEntry") -> None:
    """Notifies for..."""
    # Send Emails
    emails.CatalogueEntryLockedEmail().send_to(
        *utils.all_administrators(),  # All administrators
        *entry.editors.all(),  # All editors
        *entry.email_notifications(manager="on_lock").all(),  # type: ignore[operator]
        *entry.email_notifications(manager="both").all(),  # type: ignore[operator]
    )
