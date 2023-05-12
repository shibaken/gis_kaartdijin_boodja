"""Kaartdijin Boodja Catalogue Scan Management Command."""


# Third-Party
from django.core.management import base

# Local
from govapp.apps.catalogue import directory_scanner

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Scan Management Command."""
    # Help string
    help = "Scans the staging area to absorb files"  # noqa: A003

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Scanning staging area")

        # Go!
        directory_scanner.Scanner().scan()

