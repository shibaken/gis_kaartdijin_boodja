"""Kaartdijin Boodja Emails Django Application Functionality."""


# Standard
import logging

# Third-Party
from django import conf
from django import template
from django.contrib import auth
from django.contrib.auth import models
from django.core import mail
from django.template import loader
from django.utils import html

# Typing
from typing import Any, Optional, Union


# Logging
log = logging.getLogger(__name__)

# Shortcuts
UserModel = auth.get_user_model()


class TemplateEmailBase:
    """Base Class for a Template Email."""
    subject = ""
    html_template = "base_email.html"
    txt_template = "base_email.txt"

    def send_to_users(
        self,
        *users: Any,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Sends an email individually to many users.

        Args:
            *users (Any): Possible users to send the email to.
            context (Optional[dict[str, Any]]): Context for the template.
        """
        # Filter the supplied users to only UserModel objects, and cast them to
        # a set to eliminate any duplicates
        filtered_users = set(u for u in users if isinstance(u, UserModel))

        # Loop through users
        for user in filtered_users:
            # Send the email!
            self.send_to_user(user, context)

    def send_to_user(
        self,
        user: models.User,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Sends the email to the specified user.

        Args:
            user (models.User): User to be emailed
            context (Optional[dict[str, Any]]): Context for the template.
        """
        # Send Email
        self.send(user.email, context=context)

    def send(
        self,
        to_addresses: Union[str, list[str]],
        from_address: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        attachments: Optional[list[tuple[str, bytes, str]]] = None,
        cc: Optional[Union[str, list[str]]] = None,
        bcc: Optional[Union[str, list[str]]] = None,
    ) -> None:
        """Sends an email using EmailMultiAlternatives with text and html.

        Args:
            to_addresses (Union[str, list[str]]): Email addresses to send to.
            from_address (Optional[str]): Optional from address. If not
                supplied the settings.DEFAULT_FROM_EMAIL is used.
            context (Optional[dict[str, Any]]): Context for template rendering
            attachments (Optional[list[tuple[str, bytes, str]]]): A list of
                (filepath, content, mimetype) triples.
            cc (Optional[Union[str, list[str]]]): Optional cc addresses.
            bcc (Optional[Union[str, list[str]]]): Optional bcc addresses.
        """
        # Retrieve the HTML template
        # This will raise a TemplateDoesNotExist error if it cannot be found
        html_template = loader.get_template(self.html_template)

        # Render the HTML template
        html_body = render(html_template, context)

        # Check for an explicit text template
        if self.txt_template is not None:
            # Retrieve the text template
            # Again, this will raise an error if it cannot be found
            txt_template = loader.get_template(self.txt_template)

            # Render the text template
            txt_body = render(txt_template, context)
        else:
            # If no explicit text template is provided, then strip the HTML
            # tags from the HTML template
            txt_body = html.strip_tags(html_body)

        # Build message options
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        if attachments is None:
            attachments = []
        if attachments is not None and not isinstance(attachments, list):
            attachments = list(attachments)
        if attachments is None:
            attachments = []

        # Construct message
        msg = mail.EmailMultiAlternatives(
            subject=self.subject,
            body=txt_body,
            from_email=from_address,
            to=to_addresses,
            attachments=attachments,
            cc=cc,
            bcc=bcc,
        )
        msg.attach_alternative(html_body, "text/html")

        # Attempt to send email
        try:
            # Check settings
            if not conf.settings.DISABLE_EMAIL:
                # Send!
                msg.send(fail_silently=False)

        except Exception as exc:
            # Log
            log.exception(f"Error while sending email to {to_addresses}: {exc}")


def render(
    django_template: Union[str, template.Template],
    context: Optional[dict[str, Any]] = None,
) -> str:
    """Renders a Django template.

    Args:
        django_template (Union[str, template.Template]): Template or template
            name to render.
        context (Optional[dict[str, Any]]): Optional context for template.

    Returns:
        str: Rendered template
    """
    # Update context with settings if applicable
    if isinstance(context, dict):
        context.update({"settings": conf.settings})

    # Retrieve template if applicable
    if isinstance(django_template, str):
        django_template = template.Template(django_template)

    # Render template
    return django_template.render(context)
