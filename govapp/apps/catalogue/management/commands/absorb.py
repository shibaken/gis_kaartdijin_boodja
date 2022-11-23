"""Kaartdijin Boodja Catalogue Absorb Management Command."""


# Standard
import argparse
import pathlib

# Third-Party
from django.core.management import base

# Local
from ... import absorber

# Typing
from typing import Any


class Command(base.BaseCommand):
    """Absorb Management Command."""
    # Help string
    help = "Absorbs a file"  # noqa: A003

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds command-line arguments to the management command.

        Args:
            parser (argparse.ArgumentParser): Argument parser to add to.
        """
        # Add arguments
        parser.add_argument("file", type=pathlib.Path)

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles the management command functionality."""
        # Retrieve command-line arguments
        filepath = kwargs["file"]

        # Display information
        self.stdout.write(f"Absorbing: '{filepath}'")

        # Go!
        absorber.Absorber().absorb(filepath)
