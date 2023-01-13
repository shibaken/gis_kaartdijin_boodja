"""Model Factories for the Catalogue Workspace Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class WorkspaceFactory(factory.django.DjangoModelFactory):
    """Factory for a Workspace."""
    name = factory.Sequence(lambda n: f"Workspace {n + 1}")

    class Meta:
        """Workspace Factory Metadata."""
        model = models.workspaces.Workspace
