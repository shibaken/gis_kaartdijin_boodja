"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class CustodianSerializer(serializers.ModelSerializer):
    """Custodian Model Serializer."""
    class Meta:
        """Custodian Model Serializer Metadata."""
        model = models.custodians.Custodian
        fields = ("id", "name", "contact_name", "contact_email", "contact_phone")
        read_only_fields = ("id", "name", "contact_name", "contact_email", "contact_phone")
