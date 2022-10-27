"""Django management command to send a test email."""


# Standard
import argparse

# Third-Party
from django.core.management import base

# Local
from govapp import emails

# Typing
from typing import Any


class TestEmailCommand(base.BaseCommand):
    """Management command to send a test email."""
    # Help string for the command-line interface
    help = "Test email"  # noqa: A003

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds command-line arguments to the Django management command.

        Args:
            parser (argparse.ArgumentParser): Argument parser to add to.
        """
        # Add arguments
        parser.add_argument("-t", "--to", type=str, help="To Email Address")

    def handle(self, *args: Any, **options: Any) -> None:
        """Handles the Django management command functionality.

        Args:
            *args (Any): Positional arguments passed to the command.
            **options (Any): Keyword arguments passed to the command.
        """
        # Retrieve the "to" argument
        to_arg = options["to"]

        # Send email
        emails.sendHtmlEmail(
            to=[to_arg],
            subject="Test Email",
            context={"test": "test"},
            template="email/test-body.html",
            cc=None,
            bcc=None,
            from_email="no-reply@dbca.wa.gov.au",
            template_group="pvs",
            attachments=None,
        )
