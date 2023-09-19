"""Kaartdijin Boodja Publisher Django Application GeoserverPool Models."""


# Third-Party
from django.db import models
from django.utils import timezone
import reversion

# Local
from govapp.common import mixins

# Typing
from typing import TYPE_CHECKING

# Type Checking
if TYPE_CHECKING:
    from govapp.apps.publisher.models.publish_entries import PublishEntry

class GeoServerQueueStatus(models.IntegerChoices):
    READY = 0
    ON_PUBLISHING = 1
    PUBLISHED = 2
    FAILED = 3

@reversion.register()
class GeoServerQueue(mixins.RevisionedMixin):
    """Model for an Geoserver Queue."""
    publish_entry = models.ForeignKey(
        to="PublishEntry",
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

    def change_status(self, status:GeoServerQueueStatus) -> None:
        self.status = status
        if status == GeoServerQueueStatus.ON_PUBLISHING:
            self.started_at = timezone.now()
        elif status == GeoServerQueueStatus.PUBLISHED:
            self.completed_at = timezone.now()
        self.save()
        
    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.id}"
    
