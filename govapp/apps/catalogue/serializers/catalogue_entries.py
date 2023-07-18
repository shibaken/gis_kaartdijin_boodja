"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class CatalogueEntrySerializer(serializers.ModelSerializer):
    """Catalogue Entry Model Serializer."""
    active_layer = serializers.PrimaryKeyRelatedField(read_only=True)  # type: ignore[var-annotated]
    custodian_name = serializers.ReadOnlyField(source='custodian.name',)
    assigned_to_first_name = serializers.ReadOnlyField(source='assigned_to.first_name',)
    assigned_to_last_name = serializers.ReadOnlyField(source='assigned_to.last_name',)
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email',)

    class Meta:
        """Catalogue Entry Model Serializer Metadata."""
        model = models.catalogue_entries.CatalogueEntry
        fields = (
            "id",
            "name",
            "description",
            "status",
            "created_at",
            "updated_at",
            # "editors",
            "custodian",
            "assigned_to",
            "subscription",
            "active_layer",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
            "publish_entry",
            "custodian_name",
            "assigned_to_first_name",
            "assigned_to_last_name",
            "assigned_to_email"
        )
        read_only_fields = (
            "id",
            #"name",
            "status",
            "created_at",
            "updated_at",
            # "editors",
            "assigned_to",
            "subscription",
            "active_layer",
            "layers",
            "email_notifications",
            "webhook_notifications",
            "attributes",
            "metadata",
            "symbology",
            "publish_entry",
        )
