"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from .. import models


class CatalogueEntrySerializer(serializers.ModelSerializer):
    """Catalogue Entry Model Serializer."""
    active_layer = serializers.PrimaryKeyRelatedField(read_only=True)  # type: ignore[var-annotated]

    class Meta:
        """Catalogue Entry Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = (
            "id",
            "name",
            "description",
            "status",
            "updated_at",
            "editors",
            "custodian",
            "assigned_to",
            "workspace",
            "subscription",
            "active_layer",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
        )
        read_only_fields = (
            "id",
            "status",
            "updated_at",
            "editors",
            "assigned_to",
            "subscription",
            "active_layer",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
        )
