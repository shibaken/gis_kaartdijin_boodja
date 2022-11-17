"""Kaartdijin Boodja Catalogue Absorb Management Command."""


# Standard
import argparse

# Third-Party
from django.core.management import base

# Local
from ... import emails

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Email Management Command."""
    # Help string
    help = "Sends an email"  # noqa: A003

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds command-line arguments to the management command.

        Args:
            parser (argparse.ArgumentParser): Argument parser to add to.
        """
        # Add arguments
        parser.add_argument("to")

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Retrieve command-line arguments
        to = kwargs["to"]

        # Go!
        emails.TemplateEmailBase().send(to)
