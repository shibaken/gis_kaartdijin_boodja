"""Kaartdijin Boodja Publisher Django Application GeoserverPool Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins
from govapp.apps.publisher.models import publish_entries, geoserver_pool

class GeoServerQueueStatus(models.IntegerChoices):
    READY = 0
    ON_PUBLISHING = 1
    PUBLISHED = 2
    FAILED = 3

@reversion.register()
class GeoServerQueue(mixins.RevisionedMixin):
    """Model for an Geoserver Queue."""
    publish_entry = models.ForeignKey(
        publish_entries.PublishEntry,
        related_name="geoserver_queues",
        on_delete=models.CASCADE,
    )
    symbology_only = models.BooleanField(default=True)
    status = models.IntegerField(choices=GeoServerQueueStatus.choices, default=GeoServerQueueStatus.READY)
    publishing_result = models.TextField(null=True)
    success = models.BooleanField(null=True, default=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Geoserver Queue Model Metadata."""
        verbose_name = "Geoserver Queue"
        verbose_name_plural = "Geoserver Queues"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.id}"
