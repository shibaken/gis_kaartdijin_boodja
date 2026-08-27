"""Kaartdijin Boodja Catalogue Cleanup Pending Imports Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.catalogue import pending_imports_cleanup

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Cleanup Pending Imports Management Command."""
    # Help string
    help = "Deletes stale, abandoned chunked-upload files from the pending imports staging area"  # noqa: A003

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Cleaning up stale pending import files")

        # Go!
        pending_imports_cleanup.PendingImportsCleaner().cleanup()
