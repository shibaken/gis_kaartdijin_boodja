"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerSubmissionSerializer(serializers.ModelSerializer):
    """Layer Submission Model Serializer."""
    class Meta:
        """Layer Submission Model Serializer Metadata."""
        model = models.layer_submissions.LayerSubmission
        fields = (
            "id",
            "name",
            "description",
            "file",
            "is_active",
            "status",
            "submitted_at",
            "created_at",
            "catalogue_entry",
        )
        read_only_fields = (
            "id",
            "name",
            "description",
            "file",
            "is_active",
            "status",
            "submitted_at",
            "created_at",
            "catalogue_entry",
        )
