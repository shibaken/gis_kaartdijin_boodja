
"""Kaartdijin Boodja Catalogue Django Application Emails."""


# Local
from ..emails import emails


class CatalogueEntryCreatedEmail(emails.TemplateEmailBase):
    """Catalogue Entry Created Email Abstraction."""
    subject = "A new Catalogue Entry was created"
    html_template = "catalogue_entry_created_email.html"
    txt_template = "catalogue_entry_created_email.txt"


class CatalogueEntryUpdateSuccessEmail(emails.TemplateEmailBase):
    """Catalogue Entry Update Success Email Abstraction."""
    subject = "A Catalogue Entry update was successful"
    html_template = "catalogue_entry_update_success_email.html"
    txt_template = "catalogue_entry_update_success_email.txt"


class CatalogueEntryUpdateFailEmail(emails.TemplateEmailBase):
    """Catalogue Entry Update Fail Email Abstraction."""
    subject = "A Catalogue Entry update failed"
    html_template = "catalogue_entry_update_fail_email.html"
    txt_template = "catalogue_entry_update_fail_email.txt"
