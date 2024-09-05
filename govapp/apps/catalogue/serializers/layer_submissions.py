"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerSubmissionSerializer(serializers.ModelSerializer):
    """Layer Submission Model Serializer."""
    submitted_at_str = serializers.SerializerMethodField()
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
            "status_name",
            "submitted_at",
            "submitted_at_str",
            "created_at",
            "catalogue_entry",
            "permission_type",
            "permission_type_str",
        )
        read_only_fields = (
            "id",
            "name",
            "description",
            "file",
            "is_active",
            "status",
            "status_name",
            "submitted_at",
            "submitted_at_str",
            "created_at",
            "catalogue_entry",
            "permission_type",
            "permission_type_str",
        )

    def get_submitted_at_str(self, obj):
        if obj.submitted_at:
            return obj.submitted_at.strftime('%d/%m/%Y %H:%M:%S')
        return None