"""Kaartdijin Boodja Catalogue Django Application Layer Subscription Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue.models import catalogue_entries
from govapp.apps.publisher.models import workspaces


# class LayerSubscriptionStatus(models.IntegerChoices):
#     """Enumeration for a Layer Subscription Status."""
#     ACTIVE = 1
#     DISABLED = 2
    
class LayerSubscriptionType(models.IntegerChoices):
    """Enumeration for a Layer Subscription Status."""
    WMS = 1
    WFS = 2


@reversion.register()
class LayerSubscription(mixins.RevisionedMixin):
    """Model for a Layer Subscription."""
    type = models.IntegerField(choices=LayerSubscriptionType.choices)
    # status = models.IntegerField(choices=LayerSubscriptionStatus.choices, default=LayerSubscriptionStatus.ACTIVE)
    enabled = models.BooleanField(default=True)
    url = models.URLField()
    username = models.CharField(max_length=100)
    userpassword = models.CharField(max_length=100)
    connection_timeout = models.IntegerField(default=10000) # ms
    max_connections = models.IntegerField(default=1, null=True) # for WMS
    read_timeout = models.IntegerField(default=10000, null=True) # ms, for WMS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    catalogue_entry = models.OneToOneField(
        catalogue_entries.CatalogueEntry,
        related_name="subscription",
        on_delete=models.CASCADE)
    workspace = models.ForeignKey(
        workspaces.Workspace,
        related_name="workspace",
        on_delete=models.CASCADE)

    class Meta:
        """Layer Subscription Model Metadata."""
        verbose_name = "Layer Subscription"
        verbose_name_plural = "Layer Subscriptions"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    @property
    def name(self) -> str:
        """Proxies the Catalogue Entry's name to this model.

        Returns:
            str: Name of the Catalogue Entry.
        """
        # Retrieve and Return
        return self.catalogue_entry.name
    
    @property
    def description(self) -> str:
        """Proxies the Catalogue Entry's description to this model.

        Returns:
            str: Description of the Catalogue Entry.
        """
        # Retrieve and Return
        return self.catalogue_entry.description
