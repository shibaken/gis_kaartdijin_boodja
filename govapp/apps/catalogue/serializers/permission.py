"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models


class CatalogueEntryPermissionSerializer(serializers.ModelSerializer):
    """Catalogue Permission Model Serializer."""
    first_name = serializers.ReadOnlyField(source='user.first_name',)
    last_name = serializers.ReadOnlyField(source='user.last_name',)
    email =  serializers.ReadOnlyField(source='user.email',)
    access_permission_label = serializers.ReadOnlyField(source='get_access_permission_display',)

    class Meta:
        """Catalogue Permission Model Serializer Metadata."""
        model = models.permission.CatalogueEntryPermission
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "active",
            "access_permission",
            "access_permission_label",
        )
        read_only_fields = (
            "id",
            "first_name",
            "last_name",
            "email",
        )


class CatalogueEntryPermissionCreateSerializer(serializers.ModelSerializer):
    """Catalogue Permission Create Model Serializer."""

    class Meta:
        """Catalogue Permission Create Model Serializer Metadata."""
        model = CatalogueEntryPermissionSerializer.Meta.model
        fields = ('user', 'catalogue_entry')
        
    def validate_user(self, user):
         catalogue_entry = self.initial_data.get('catalogue_entry')
         if models.permission.CatalogueEntryPermission.objects.filter(catalogue_entry=catalogue_entry, user=user).exists():
             raise serializers.ValidationError("Value '{}' of 'user' is already taken.".format(f"{user.first_name} {user.last_name}"))
         return user
