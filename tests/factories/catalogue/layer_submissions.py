"""Model Factories for the Catalogue Layer Submission Model."""


# Standard
import datetime

# Third-Party
import factory
import factory.fuzzy

# Local
from govapp.apps.catalogue import models


class LayerSubmissionFactory(factory.django.DjangoModelFactory):
    """Factory for a Layer Submission."""
    name = factory.Sequence(lambda n: f"Layer Submission {n + 1}")
    description = factory.Faker("paragraph")
    file = factory.Faker("uri")
    status = factory.fuzzy.FuzzyChoice(models.layer_submissions.LayerSubmissionStatus)
    submitted_at = factory.Faker("date_time_this_year", tzinfo=datetime.timezone.utc)

    class Meta:
        """Layer Submission Factory Metadata."""
        model = models.layer_submissions.LayerSubmission
