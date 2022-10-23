"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from .. import models


class CatalogueEntrySerializer(serializers.ModelSerializer):
    """Catalogue Entry Model Serializer."""
    class Meta:
        """Catalogue Entry Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = (
            "id",
            "name",
            "description",
            "status",
            "updated_at",
            "custodian",
            "assigned_to",
            "subscription",
            "active_layer",
            "layers",
            "email_notifications",
            "webhook_notifications",
        )
