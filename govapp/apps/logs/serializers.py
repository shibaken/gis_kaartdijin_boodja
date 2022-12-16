"""Kaartdijin Boodja Logs Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from . import models


class CommunicationsLogDocumentSerializer(serializers.ModelSerializer):
    """Communications Log Document Model Serializer."""
    class Meta:
        """Communications Log Document Model Serializer Metadata."""
        model = models.CommunicationsLogDocument
        fields = (
            "id",
            "name",
            "description",
            "uploaded_at",
            "entry",
            "file",
        )
        read_only_fields = (
            "uploaded_at",
            "entry",
        )


class CommunicationsLogEntrySerializer(serializers.ModelSerializer):
    """Communications Log Entry Model Serializer."""
    documents = CommunicationsLogDocumentSerializer(many=True)

    class Meta:
        """Communications Log Entry Model Serializer Metadata."""
        model = models.CommunicationsLogEntry
        fields = (
            "id",
            "created_at",
            "type",
            "to",
            "cc",
            "fromm",
            "subject",
            "text",
            "documents",
        )
        read_only_fields = (
            "documents",
        )
