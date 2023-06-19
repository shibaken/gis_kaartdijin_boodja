"""Kaartdijin Boodja Catalogue Django Application Layer Metadata Models."""


# Third-Party
from enum import Enum
from django.db import models
from django.db import connection
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue.models import catalogue_entries


@reversion.register()
class LayerAttributeType(mixins.RevisionedMixin):
    """Model for a Layer Attribute Types."""
    key = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Layer Attribute Types Model Metadata."""
        verbose_name = "Layer Attribute Types"
        verbose_name_plural = "Layer Attribute Types"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        """Stores data using dynamic default value.
        Sets value of name as same with value of key when the name does not exist
        """
        if not self.name:
            self.name = self.key
        super().save(*args, **kwargs)
        

class LayerAttributeTypeEnum(Enum):
    STRING      = 'String'
    INTEGER     = 'Integer'
    REAL        = 'Real'
    DATETIME    = 'DateTime'

def add_initial_types(sender, **kwargs):
    # # check if the table exists
    # connection.cursor.execute("SELECT to_regclass('catalogue_layerattributetype')")
    # result = connection.cursor.fetchone()
    # if result[0] is None:
    #     return
    
    # add initial data by Enum
    if sender.name == "govapp.apps.catalogue":
        for type in LayerAttributeTypeEnum:
            LayerAttributeType.objects.get_or_create(key=type.value)
            # LayerAttributeType(key=type.value).save()