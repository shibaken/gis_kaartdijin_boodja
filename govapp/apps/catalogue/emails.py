"""Kaartdijin Boodja Catalogue Django Application Emails."""


# Local
from govapp.apps.emails import emails


class CatalogueEntryLockedEmail(emails.TemplateEmailBase):
    """Catalogue Entry Locked Email Abstraction."""
    subject = "Kaartdijin Boodja Catalogue Entry locked"
    html_template = "catalogue_entry_locked_email.html"
    txt_template = "catalogue_entry_locked_email.txt"


class CatalogueEntryCreatedEmail(emails.TemplateEmailBase):
    """Catalogue Entry Created Email Abstraction."""
    subject = "Kaartdijin Boodja Catalogue Entry created"
    html_template = "catalogue_entry_created_email.html"
    txt_template = "catalogue_entry_created_email.txt"


class CatalogueEntryUpdateSuccessEmail(emails.TemplateEmailBase):
    """Catalogue Entry Update Success Email Abstraction."""
    subject = "Kaartdijin Boodja Catalogue Entry updated"
    html_template = "catalogue_entry_update_success_email.html"
    txt_template = "catalogue_entry_update_success_email.txt"


class CatalogueEntryUpdateFailEmail(emails.TemplateEmailBase):
    """Catalogue Entry Update Fail Email Abstraction."""
    subject = "Kaartdijin Boodja Catalogue Entry update failed"
    html_template = "catalogue_entry_update_fail_email.html"
    txt_template = "catalogue_entry_update_fail_email.txt"


class FileAbsorbFailEmail(emails.TemplateEmailBase):
    """File Absorb Fail Email Abstraction."""
    subject = "Kaartdijin Boodja file absorption failed"
    html_template = "file_absorb_fail_email.html"
    txt_template = "file_absorb_fail_email.txt"
