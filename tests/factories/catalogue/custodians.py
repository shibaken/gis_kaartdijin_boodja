"""Model Factories for the Catalogue Custodian Model."""


# Third-Party
import factory

# Local
from govapp.apps.catalogue import models


class CustodianFactory(factory.django.DjangoModelFactory):
    """Factory for a Custodian."""
    name = factory.Sequence(lambda n: f"Custodian {n + 1}")
    contact_name = factory.Faker("name")
    contact_email = factory.LazyAttribute(lambda a: f"{a.contact_name.replace(' ', '.')}@example.com".lower())
    contact_phone = factory.Faker("phone_number")

    class Meta:
        """Custodian Factory Metadata."""
        model = models.custodians.Custodian
