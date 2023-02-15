"""Model Factories for the Catalogue Workspace Model."""


# Third-Party
import factory

# Local
from govapp.apps.publisher import models


class WorkspaceFactory(factory.django.DjangoModelFactory):
    """Factory for a Workspace."""
    name = "default"  # Hardcode to default for unit tests

    class Meta:
        """Workspace Factory Metadata."""
        model = models.workspaces.Workspace
