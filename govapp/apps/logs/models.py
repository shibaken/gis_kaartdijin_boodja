"""Kaartdijin Boodja Logs Django Application Models."""


# Third-Party
from django.contrib import auth
from django.contrib.contenttypes import fields
from django.contrib.contenttypes import models as ct_models
from django.db import models


# Shortcuts
UserModel = auth.get_user_model()


class CommunicationsLogEntryType(models.IntegerChoices):
    """Enumeration for a Communications Log Entry Type."""
    EMAIL = 1
    PHONE = 2
    MAIL = 3
    PERSON = 4
    OTHER = 5


class CommunicationsLogEntry(models.Model):
    """Model for a Communications Log Entry."""
    # Generic Foreign Key
    # See: https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(ct_models.ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey("content_type", "object_id")

    # Communications Log Entry Fields
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=CommunicationsLogEntryType.choices)  # noqa: A003
    to = models.TextField(blank=True)
    cc = models.TextField(blank=True)
    fromm = models.TextField(blank=True)
    subject = models.TextField(blank=True)
    text = models.TextField(blank=True)

    class Meta:
        """Communications Log Entry Model Metadata."""
        verbose_name = "Communications Log Entry"
        verbose_name_plural = "Communications Log Entries"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.content_type.name} - {self.content_object}"


class CommunicationsLogDocument(models.Model):
    """Model for a Communications Log Document."""
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    entry = models.ForeignKey(CommunicationsLogEntry, related_name="documents", on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents")

    class Meta:
        """Communications Log Document Model Metadata."""
        verbose_name = "Communications Log Document"
        verbose_name_plural = "Communications Log Documents"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.file}"


class ActionsLogEntry(models.Model):
    """Model for an Actions Log Entry."""
    # Generic Foreign Key
    # See: https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(ct_models.ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey("content_type", "object_id")

    # Actions Log Entry Fields
    who = models.ForeignKey(UserModel, related_name="actions_log_entries", on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
    what = models.TextField()

    class Meta:
        """Actions Log Entry Model Metadata."""
        verbose_name = "Actions Log Entry"
        verbose_name_plural = "Actions Log Entries"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.content_object}"
