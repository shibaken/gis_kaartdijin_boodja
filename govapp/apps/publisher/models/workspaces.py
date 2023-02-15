"""Kaartdijin Boodja Publisher Django Application Workspace Models."""


# Third-Party
from django.db import models
import reversion

# Local
from govapp.common import mixins


@reversion.register()
class Workspace(mixins.RevisionedMixin):
    """Model for a Workspace."""
    name = models.TextField()

    class Meta:
        """Workspace Model Metadata."""
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"
