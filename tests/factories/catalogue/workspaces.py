"""Model Factories for the Catalogue Workspace Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class WorkspaceFactory(factory.django.DjangoModelFactory):
    """Factory for a Workspace."""
    name = "default"  # Hardcode to default for unit tests

    class Meta:
        """Workspace Factory Metadata."""
        model = models.workspaces.Workspace
