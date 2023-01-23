"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class LayerSymbologySerializer(serializers.ModelSerializer):
    """Layer Symbology Model Serializer."""
    class Meta:
        """Layer Symbology Model Serializer Metadata."""
        model = models.layer_symbology.LayerSymbology
        fields = ("id", "name", "sld", "catalogue_entry")
        read_only_fields = ("id", "name", "catalogue_entry")
