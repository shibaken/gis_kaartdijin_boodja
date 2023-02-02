"""Kaartdijin Boodja Publisher Django Application Emails."""


# Local
from govapp.apps.emails import emails


class PublishEntryLockedEmail(emails.TemplateEmailBase):
    """Publish Entry Locked Email Abstraction."""
    subject = "Kaartdijin Boodja Publish Entry locked"
    html_template = "publish_entry_locked_email.html"
    txt_template = "publish_entry_locked_email.txt"


class PublishEntryPublishSuccessEmail(emails.TemplateEmailBase):
    """Publish Entry Publish Success Email Abstraction."""
    subject = "Kaartdijin Boodja Publish Entry published"
    html_template = "publish_entry_publish_success_email.html"
    txt_template = "publish_entry_publish_success_email.txt"


class PublishEntryPublishFailEmail(emails.TemplateEmailBase):
    """Publish Entry Publish Fail Email Abstraction."""
    subject = "Kaartdijin Boodja Publish Entry failed to publish"
    html_template = "publish_entry_publish_fail_email.html"
    txt_template = "publish_entry_publish_fail_email.txt"
