"""Kaartdijin Boodja Catalogue Django Application Notification Models."""


# Third-Party
from django.db import models
from django.contrib import auth
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue.models import catalogue_entries

# Shortcuts
UserModel = auth.get_user_model()


class CatalogueEntryAccessPermission(models.IntegerChoices):
    # NONE = 1, 'None'
    READ = 2, 'Read'
    READ_WRITE = 3, 'Read and Write'


@reversion.register()
class CatalogueEntryPermission(mixins.RevisionedMixin):
    catalogue_entry = models.ForeignKey(
        catalogue_entries.CatalogueEntry, 
        related_name="catalogue_permissions", 
        on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    access_permission = models.IntegerField(choices=CatalogueEntryAccessPermission.choices, default=CatalogueEntryAccessPermission.READ)
    
    def __str__(self):
        return f'CEP{self.id}: for CE{self.catalogue_entry.id} for {self.user}'
    
    class Meta:
        unique_together = ('user', 'catalogue_entry')
